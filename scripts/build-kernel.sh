#!/bin/bash
# Fedora kernel + packages/kernel patches, built into output/RPMS.
#
# The spec is Fedora's own (src.fedoraproject.org/rpms/kernel), so it is not
# kept here. This clones Fedora dist-git into work/kernel, checks out the
# pinned f45 commit on a local "dell-ptl" branch, applies kernel.spec.diff
# (buildid .dellptl + Patch1001-1003) and copies the patches next to it.
#
# Usage: scripts/build-kernel.sh [prep|srpm]
#   prep  only prepare and run %prep
#   srpm  write a source RPM for COPR into output/srpm/kernel; COPR cannot
#         pass --without flags, so they are written into the spec copy
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

without=(debug debuginfo realtime perf libperf tools ynl selftests kabichk
         zfcpdump cross_headers efiuki)

if [[ ${1:-} == srpm ]]; then
  mkdir -p "$out/srpm/kernel"
  rm -f "$out"/srpm/kernel/*.src.rpm
  { for w in "${without[@]}"; do echo "%define _without_$w 1"; done
    cat kernel.spec; } > kernel-copr.spec
  rpmbuild -bs --define "_sourcedir $work" --define "_srcrpmdir $out/srpm/kernel" \
    kernel-copr.spec
  rm -f kernel-copr.spec
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
