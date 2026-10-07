#!/bin/bash
# Turn a Fedora kernel dist-git checkout into the .dellptl kernel: set the
# buildid and release, add the patches listed in packages/kernel/series and
# append packages/kernel/kernel-local. It edits Fedora's spec by its anchors
# rather than applying a fixed diff, so it keeps working on newer Fedora
# kernels as long as the patches themselves still apply.
#
# Usage: scripts/kernel-apply.sh <dist-git dir>
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
pkg=$root/packages/kernel
dir=${1:?usage: $0 <kernel dist-git dir>}
spec=$dir/kernel.spec

local_release=$(sed -n 's/^local_release=//p' "$pkg/fedora-base")
: "${local_release:?local_release missing in fedora-base}"

mapfile -t patches < <(grep -vE '^[[:space:]]*(#|$)' "$pkg/series")

for anchor in '^# define buildid \.local$' '^%define pkgrelease [0-9]+$' \
              '^%define specrelease [0-9]+%\{\?buildid\}%\{\?dist\}$' \
              '^Patch999999: linux-kernel-test\.patch$' \
              '^ApplyOptionalPatch linux-kernel-test\.patch$'; do
  if ! grep -qE "$anchor" "$spec"; then
    echo "kernel.spec has no line matching: $anchor" >&2
    exit 1
  fi
done

patch_defs=""
apply_lines=""
n=1001
for p in "${patches[@]}"; do
  cp "$pkg/$p" "$dir/"
  patch_defs+="Patch$n: $p\n"
  apply_lines+="ApplyOptionalPatch $p\n"
  n=$((n + 1))
done

sed -i -E \
  -e 's/^# define buildid \.local$/%define buildid .dellptl/' \
  -e "s/^(%define pkgrelease [0-9]+)$/\1.$local_release/" \
  -e "s/^%define specrelease ([0-9]+)(%\{\?buildid\}%\{\?dist\})$/%define specrelease \1.$local_release\2/" \
  -e "s/^(Patch999999: linux-kernel-test\.patch)$/# Dell XPS Panther Lake patches (packages\/kernel\/series)\n$patch_defs\n\1/" \
  -e "s/^(ApplyOptionalPatch linux-kernel-test\.patch)$/$apply_lines\1/" \
  "$spec"

grep -vE '^[[:space:]]*$' "$pkg/kernel-local" >> "$dir/kernel-local"

rpmspec -q --srpm --qf '%{name}-%{version}-%{release}\n' "$spec" 2>/dev/null | head -1
