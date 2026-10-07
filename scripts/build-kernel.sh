#!/bin/bash
# Fedora kernel + packages/kernel patches -> output/RPMS.
#
# The spec is Fedora's own (src.fedoraproject.org/rpms/kernel), so it is not
# kept here. This clones Fedora dist-git into work/kernel, checks out the
# pinned f45 commit on a local "dell-ptl" branch, applies kernel.spec.diff
# (buildid .dellptl + Patch1001-1003) and copies the patches next to it.
#
# Usage: scripts/build-kernel.sh [prep]      prep = only prepare + %prep
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
pkg=$root/packages/kernel
work=$root/work/kernel
out=$root/output
# f45 commit of the Fedora build the patches sit on (kernel-7.2.9-300);
# bump together with kernel.spec.diff
fedora_ref=45fb77a73

mkdir -p "$out/RPMS" "$out/logs"

if [[ ! -d $work/.git ]]; then
  fedpkg clone -a kernel "$work"
fi
cd "$work"
git fetch -q origin
if ! git rev-parse -q --verify dell-ptl >/dev/null; then
  git checkout -q -b dell-ptl "$fedora_ref"
  git apply "$pkg/kernel.spec.diff"
  cp "$pkg"/*.patch .
  git add kernel.spec kernel-local ./*.patch
  git commit -q -s -m "Add Dell XPS Panther Lake patches with buildid dellptl."
else
  git checkout -q dell-ptl
fi
fedpkg sources >/dev/null

mode=-bb
[[ ${1:-} == prep ]] && mode=-bp

rpmbuild $mode \
  --define "_sourcedir $work" --define "_specdir $work" \
  --define "_builddir $work/build" --define "_rpmdir $out/RPMS" \
  --target x86_64 \
  --without debug --without debuginfo --without realtime \
  --without perf --without libperf --without tools --without ynl \
  --without selftests --without kabichk --without zfcpdump \
  --without cross_headers --without efiuki \
  kernel.spec 2>&1 | tee "$out/logs/kernel.log"

ls -1 "$out/RPMS/x86_64/" | grep '^kernel' || true
