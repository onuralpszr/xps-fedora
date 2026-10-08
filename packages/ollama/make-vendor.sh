#!/bin/bash
# Build the Go module vendor archive for the ollama SRPM. Run by
# .copr/Makefile after spectool has downloaded Source0, so the COPR SRPM
# step needs no prebuilt vendor archive in this repository.
#
# Usage: make-vendor.sh <package dir> <spec>
set -euo pipefail

pkgdir=$1
spec=$2
version=$(rpmspec -q --srpm --qf '%{version}' "$spec")
out=$pkgdir/ollama-$version-vendor.tar.xz
[[ -e $out ]] && exit 0

command -v go >/dev/null || dnf -y install golang
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xzf "$pkgdir/ollama-$version.tar.gz" -C "$tmp"
(cd "$tmp/ollama-$version" && GOTOOLCHAIN=local GOFLAGS=-mod=mod go mod vendor)
tar -C "$tmp/ollama-$version" -cJf "$out" vendor
