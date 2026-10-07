#!/bin/bash
# Build one package from packages/<name>/ into output/.
# Remote sources (Source URLs in the spec) are fetched with spectool, local
# ones (patches, config) are read straight from the package directory, the
# same way COPR builds from a spec + sources.
#
# Usage: scripts/build-rpm.sh <package> [extra rpmbuild args...]
#   scripts/build-rpm.sh intel-npu-driver
#   scripts/build-rpm.sh intel-ipu7-camera --without foo
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
pkg=${1:?usage: $0 <package> [rpmbuild args]}
shift
pkgdir=$root/packages/$pkg
spec=$(ls "$pkgdir"/*.spec)
out=$root/output
srcdir=$root/work/sources/$pkg

mkdir -p "$srcdir" "$out/RPMS" "$out/SRPMS" "$out/logs"

# Local files + downloaded tarballs share one source dir
cp -a "$pkgdir"/. "$srcdir"/
spectool -g -C "$srcdir" "$spec" >/dev/null

rpmbuild -ba \
  --define "_sourcedir $srcdir" \
  --define "_specdir $srcdir" \
  --define "_builddir $root/work/build/$pkg" \
  --define "_buildrootdir $root/work/buildroot" \
  --define "_rpmdir $out/RPMS" \
  --define "_srcrpmdir $out/SRPMS" \
  "$@" "$srcdir/$(basename "$spec")" 2>&1 | tee "$out/logs/$pkg.log"

echo "== built:"
grep -E '^Wrote: ' "$out/logs/$pkg.log" | sed 's/^Wrote: /  /'
