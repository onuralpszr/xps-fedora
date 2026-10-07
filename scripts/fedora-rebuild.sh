#!/bin/bash
# Rebuild an unchanged Fedora package against our COPR stack (for example
# packages linking libonnxruntime after the onnxruntime update).
#
# Takes the package from Fedora dist-git (branch f45 by default), expands
# %autorelease/%autochangelog into a static spec, appends a release suffix so
# the rebuild sorts above Fedora's build, adds a changelog entry, fetches the
# lookaside sources and writes an SRPM to output/rebuild/<pkg>/. With
# --mock it is then built like scripts/mock-build.sh does.
#
# Usage: scripts/fedora-rebuild.sh <package> [--mock] [-- extra mock args]
#   scripts/fedora-rebuild.sh vcmi --mock
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
pkg=${1:?usage: $0 <package> [--mock] [-- mock args]}
shift
do_mock=0
if [ "${1:-}" = "--mock" ]; then do_mock=1; shift; fi
[ "${1:-}" = "--" ] && shift

branch=${FEDORA_BRANCH:-f45}
suffix=${REBUILD_SUFFIX:-1.ovstack}
reason=${REBUILD_REASON:-"Rebuild for onnxruntime 1.30 / onnx 1.22 / OpenVINO 2026.4"}
packager="Onuralp SEZER <thunderbirdtr@fedoraproject.org>"

work=$root/work/rebuild/$branch/$pkg
out=$root/output/rebuild/$branch/$pkg
rm -rf "$work"
mkdir -p "$out"
if git clone -q --depth 200 -b "$branch" "https://src.fedoraproject.org/rpms/$pkg.git" "$work" 2>/dev/null; then
  from=distgit
  cd "$work"
  # Static Release/changelog from dist-git history
  rpmautospec process-distgit "$pkg.spec" "$pkg.spec" 2>/dev/null || :
elif rf_branch=$([ "$branch" = rawhide ] && echo master || echo "$branch") &&
     { git clone -q --depth 50 -b "$rf_branch" "https://github.com/rpmfusion/$pkg.git" "$work" 2>/dev/null ||
       git clone -q --depth 50 -b "$rf_branch" "https://github.com/rpmfusion/$pkg-nonfree.git" "$work" 2>/dev/null; }; then
  # RPM Fusion git (rawhide = master): static Release, sources fetched by URL
  from=rpmfusion
  cd "$work"
else
  # Neither: start from the source RPM of whichever enabled repo ships it;
  # its spec is already expanded
  from=srpm
  mkdir -p "$work" && cd "$work"
  dnf -q download --source --destdir "$work" "$pkg" >/dev/null
  rpm2cpio "$work"/*.src.rpm | cpio -idm --quiet
  rm -f "$work"/*.src.rpm
fi

# Release: N%{?dist} -> N%{?dist}.<suffix>
sed -i -E "0,/^Release:/s/^(Release:[[:space:]]*.*)$/\1.${suffix}/" "$pkg.spec"
evr=$(rpmspec -q --srpm --qf '%{evr}\n' "$pkg.spec" 2>/dev/null | head -1)
date=$(LC_ALL=C date +'%a %b %d %Y')
sed -i "/^%changelog/a * ${date} ${packager} - ${evr}\n- ${reason}\n" "$pkg.spec"

case $from in
  distgit)   fedpkg --release "$branch" sources >/dev/null ;;
  rpmfusion)
    # RPM Fusion lookaside, same layout as Fedora's; spectool for anything else
    repo_name=$(basename "$(git remote get-url origin)" .git)
    section=$([[ $repo_name == *-nonfree ]] && echo nonfree || echo free)
    while read -r algo file _ hash; do
      file=${file#(}; file=${file%)}
      curl -sfL -o "$file" \
        "https://pkgs.rpmfusion.org/repo/pkgs/$section/$pkg/$file/${algo,,}/$hash/$file" || :
    done < <(grep -E '^SHA512 \(' sources 2>/dev/null)
    spectool -g -C "$work" "$pkg.spec" >/dev/null 2>&1 || : ;;
esac
rpmbuild -bs --define "_sourcedir $work" --define "_srcrpmdir $out" "$pkg.spec" >/dev/null
srpm=$(ls -t "$out"/*.src.rpm | head -1)
echo "== $srpm"

if [ $do_mock = 1 ]; then
  repo=$root/output/repo
  mock -r "${MOCK_CHROOT:-fedora-45-x86_64}" --resultdir "$out" \
    --addrepo "file://$repo" "$@" --rebuild "$srpm"
  cp "$out"/*.rpm "$repo"/ && rm -f "$repo"/*.src.rpm
  createrepo_c -q --update "$repo"
fi
