#!/bin/bash
# Find Fedora updates that need a rebuild in the COPR. Used by the daily
# Upstream watch workflow, and safe to run by hand.
#
# Usage:
#   scripts/upstream-watch.sh kernel     newest Fedora 45 kernel in Bodhi
#                                        (testing or stable) and its dist-git
#                                        commit, compared to fedora-base
#   scripts/upstream-watch.sh bump-kernel <nvr> <commit>
#                                        point packages/kernel/fedora-base at
#                                        that Fedora kernel, local release 1
#   scripts/upstream-watch.sh rebuilds   packages rebuilt against our
#                                        onnxruntime whose Fedora or RPM
#                                        Fusion version is now newer than the
#                                        COPR rebuild (needs dnf)
#
# Results also go to $GITHUB_OUTPUT when it is set.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
base=$root/packages/kernel/fedora-base
release=${FEDORA_RELEASE:-45}
copr_owner=${COPR_OWNER:-thunderbirdtr}

# Fedora packages linking libonnxruntime that the COPR carries rebuilds of
rebuilt=(calibre crow-translate gstreamer1-plugins-bad-free monado pipewire vcmi)

output() {
  echo "$1=$2"
  if [[ -n ${GITHUB_OUTPUT:-} ]]; then echo "$1=$2" >> "$GITHUB_OUTPUT"; fi
}

case ${1:-} in
kernel)
  fedora_nvr=$(sed -n 's/^fedora_nvr=//p' "$base")
  latest=$(curl -fsS "https://bodhi.fedoraproject.org/updates/?packages=kernel&releases=F$release&rows_per_page=10" |
    python3 -c '
import json, sys
for u in json.load(sys.stdin)["updates"]:
    if u["status"] in ("testing", "stable"):
        for b in u["builds"]:
            if b["nvr"].startswith("kernel-"):
                print(b["nvr"].rsplit(".", 1)[0])
                sys.exit()
')
  output current "$fedora_nvr"
  output latest "$latest"
  if [[ -z $latest || $latest == "$fedora_nvr" ]]; then
    output new false
    exit 0
  fi
  if [[ $(printf '%s\n%s\n' "$fedora_nvr" "$latest" | sort -V | tail -1) != "$latest" ]]; then
    output new false
    exit 0
  fi
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  git clone -q --depth 50 --no-checkout -b "f$release" \
    https://src.fedoraproject.org/rpms/kernel.git "$tmp/kernel"
  log=$(git -C "$tmp/kernel" log --format='%h %s')
  ref=$(awk -v s="$latest" '$2 == s {print $1; exit}' <<< "$log")
  if [[ -z $ref ]]; then
    echo "no dist-git commit named $latest on f$release" >&2
    exit 1
  fi
  output ref "$ref"
  output new true
  ;;

bump-kernel)
  nvr=${2:?nvr}
  ref=${3:?commit}
  sed -i -E -e "s/^fedora_ref=.*/fedora_ref=$ref/" \
            -e "s/^fedora_nvr=.*/fedora_nvr=$nvr/" \
            -e "s/^local_release=.*/local_release=1/" "$base"
  grep -E '^[a-z_]+=' "$base"
  ;;

rebuilds)
  copr_repo=https://download.copr.fedorainfracloud.org/results/$copr_owner/intel-ai-stack/fedora-$release-x86_64/
  stale=()
  for pkg in "${rebuilt[@]}"; do
    fedora=$(dnf -q repoquery --latest-limit 1 --qf '%{evr}\n' \
      --disablerepo='copr:*' "$pkg" 2>/dev/null | sort -V | tail -1)
    ours=$(dnf -q repoquery --latest-limit 1 --qf '%{evr}\n' \
      --repofrompath="watch-copr,$copr_repo" --repo=watch-copr "$pkg" 2>/dev/null | tail -1)
    # 9.14.0-1.fc45.1.ovstack is our rebuild of Fedora's 9.14.0-1.fc45
    ours_base=${ours%.1.ovstack}
    echo "$pkg: fedora ${fedora:-none}, copr ${ours:-none}"
    [[ -z $fedora ]] && continue
    if [[ -z $ours ]]; then stale+=("$pkg"); continue; fi
    # rpmdev-vercmp exits 0 when equal, 11 when ours is newer, 12 when older
    rc=0
    rpmdev-vercmp "$ours_base" "$fedora" >/dev/null || rc=$?
    if [[ $rc -eq 12 ]]; then stale+=("$pkg"); fi
  done
  output stale "${stale[*]}"
  ;;

*)
  sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
  ;;
esac
