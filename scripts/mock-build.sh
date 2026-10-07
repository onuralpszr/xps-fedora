#!/bin/bash
# Build one package from packages/<name>/ in a clean mock chroot, the way
# COPR builds it. Results land in output/mock/<name>/ and are added to the
# local repo output/repo/, which later mock builds use, so packages that
# depend on each other (openvino, then openvino-tokenizers, then openvino-genai)
# can be chained before they exist in COPR.
#
# Usage: scripts/mock-build.sh <package> [extra mock args...]
#   scripts/mock-build.sh openvino
#   scripts/mock-build.sh llama-cpp --with vulkan
# Needs membership in the mock group (sudo usermod -aG mock $USER).
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
pkg=${1:?usage: $0 <package> [mock args]}
shift
pkgdir=$root/packages/$pkg
spec=$(ls "$pkgdir"/*.spec)
srcdir=$root/work/sources/$pkg
resultdir=$root/output/mock/$pkg
repo=$root/output/repo
chroot=${MOCK_CHROOT:-fedora-45-x86_64}

mkdir -p "$srcdir" "$resultdir" "$repo"
rm -f "$resultdir"/*.log "$resultdir"/*.rpm
[ -d "$repo/repodata" ] || createrepo_c -q "$repo"

cp -a "$pkgdir"/. "$srcdir"/
spectool -g -C "$srcdir" "$spec" >/dev/null

rpmbuild -bs \
  --define "_sourcedir $srcdir" \
  --define "_srcrpmdir $resultdir" \
  "$srcdir/$(basename "$spec")" >/dev/null
srpm=$(ls -t "$resultdir"/*.src.rpm | head -1)

mock -r "$chroot" --resultdir "$resultdir" \
  --addrepo "file://$repo" \
  "$@" --rebuild "$srpm"

cp "$resultdir"/*.rpm "$repo"/
rm -f "$repo"/*.src.rpm
createrepo_c -q --update "$repo"

echo "== built:"
ls "$resultdir"/*.rpm | sed 's|^|  |'
