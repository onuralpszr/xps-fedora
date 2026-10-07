#!/bin/bash
# Fedora kernel + packages/kernel patches, built into output/RPMS.
#
# The spec is Fedora's own (src.fedoraproject.org/rpms/kernel), so it is not
# kept here. This clones Fedora dist-git into work/kernel-<release>, checks
# out the f45 commit from packages/kernel/fedora-base and runs
# scripts/kernel-apply.sh on it (buildid .dellptl, release, the patches from
# packages/kernel/series and kernel-local). Nothing is committed there.
#
# Usage: scripts/build-kernel.sh [prep|srpm]
#   prep  only prepare and run %prep
#   srpm  write a source RPM for COPR into output/srpm/kernel; COPR cannot
#         pass --without flags, so they are written into the spec copy
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
pkg=$root/packages/kernel
out=$root/output

fedora_ref=$(sed -n 's/^fedora_ref=//p' "$pkg/fedora-base")
fedora_nvr=$(sed -n 's/^fedora_nvr=//p' "$pkg/fedora-base")
local_release=$(sed -n 's/^local_release=//p' "$pkg/fedora-base")
# one work tree per Fedora base and local release, left uncommitted
work=${KERNEL_WORK:-$root/work/kernel-${fedora_nvr#kernel-}.$local_release}

mkdir -p "$out/RPMS" "$out/logs"

if [[ ! -e $work/.dellptl-applied ]]; then
  rm -rf "$work"
  git clone -q --depth 50 -b f45 https://src.fedoraproject.org/rpms/kernel.git "$work"
  cd "$work"
  if ! git cat-file -e "$fedora_ref^{commit}" 2>/dev/null; then
    git fetch -q --unshallow origin
  fi
  git checkout -q -B dellptl "$fedora_ref"
  "$root/scripts/kernel-apply.sh" "$work"
  touch .dellptl-applied
fi
cd "$work"
fedpkg sources >/dev/null

without=(debug debuginfo realtime perf libperf tools ynl selftests kabichk
         zfcpdump cross_headers efiuki)

if [[ ${1:-} == srpm ]]; then
  # COPR's import cannot serve empty source files (the Module.kabi_* lists,
  # unused with kabichk off), so stage a copy where they hold a newline
  stage=$root/work/kernel-srpm
  rm -rf "$stage" && mkdir -p "$stage" "$out/srpm/kernel"
  find . -maxdepth 1 -type f -not -name '.*' -exec cp -l {} "$stage"/ \;
  find "$stage" -maxdepth 1 -type f -empty -exec sh -c 'rm "$1" && echo > "$1"' _ {} \;
  { for w in "${without[@]}"; do echo "%define _without_$w 1"; done
    cat kernel.spec; } > "$stage/kernel.spec.new"
  mv "$stage/kernel.spec.new" "$stage/kernel.spec"
  rm -f "$out"/srpm/kernel/*.src.rpm
  rpmbuild -bs --define "_sourcedir $stage" --define "_srcrpmdir $out/srpm/kernel" \
    "$stage/kernel.spec"
  rm -rf "$stage"
  exit 0
fi

mode=-bb
[[ ${1:-} == prep ]] && mode=-bp
without_flags=()
for w in "${without[@]}"; do without_flags+=(--without "$w"); done

rpmbuild $mode \
  --define "_sourcedir $work" --define "_specdir $work" \
  --define "_builddir $work/build" --define "_rpmdir $out/RPMS" \
  --target x86_64 \
  "${without_flags[@]}" \
  kernel.spec 2>&1 | tee "$out/logs/kernel.log"

for f in "$out"/RPMS/x86_64/kernel*; do
  if [[ -e $f ]]; then basename "$f"; fi
done
