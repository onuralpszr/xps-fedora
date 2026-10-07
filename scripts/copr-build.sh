#!/bin/bash
# Submit packages from packages/<name>/ to COPR as SRPMs.
#
# Usage:
#   scripts/copr-build.sh <package> [copr-cli build args...]
#   scripts/copr-build.sh --batch "pkg1 pkg2" [--after <build-id>] [args...]
#
# A batch builds in parallel; --after makes it wait for the batch that
# <build-id> belongs to, which is how dependent packages are chained
# (copr-cli --after-build-id / --with-build-id). Prints the build IDs.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
project=${COPR_PROJECT:-thunderbirdtr/intel-ai-stack}
timeout=${COPR_TIMEOUT:-72000}   # 20 h; openvino/onnxruntime are long

srpm_for() {
  local pkg=$1 pkgdir=$root/packages/$1 srcdir=$root/work/sources/$1 out=$root/output/srpm/$1
  mkdir -p "$srcdir" "$out"
  rm -f "$out"/*.src.rpm
  cp -a "$pkgdir"/. "$srcdir"/
  local spec; spec=$(ls "$pkgdir"/*.spec)
  spectool -g -C "$srcdir" "$spec" >/dev/null
  rpmbuild -bs --define "_sourcedir $srcdir" --define "_srcrpmdir $out" \
    --define "dist %{nil}" "$srcdir/$(basename "$spec")" >/dev/null
  ls "$out"/*.src.rpm
}

submit() {   # submit <srpm> [extra args] -> prints build id
  copr-cli build --nowait --timeout "$timeout" "$project" "$@" 2>&1 |
    sed -n 's/^Created builds: *//p'
}

if [ "${1:-}" = "--batch" ]; then
  pkgs=$2; shift 2
  after=""
  if [ "${1:-}" = "--after" ]; then after=$2; shift 2; fi
  first=""
  for p in $pkgs; do
    srpm=$(srpm_for "$p")
    if [ -z "$first" ]; then
      id=$(submit "$srpm" ${after:+--after-build-id "$after"} "$@")
      first=$id
    else
      id=$(submit "$srpm" --with-build-id "$first" "$@")
    fi
    echo "$p $id"
  done
else
  pkg=${1:?usage: $0 <package> | --batch "pkgs" [--after id]}; shift
  echo "$pkg $(submit "$(srpm_for "$pkg")" "$@")"
fi
