# COPR "make srpm" recipe. COPR clones this repository and runs
#   make -f .copr/Makefile srpm outdir=<dir> spec=<path to spec>
# for a package registered with --method make_srpm and --subdir packages/<name>.
# Remote sources come from their Source URLs, local files from the package
# directory, the same way scripts/copr-build.sh builds an SRPM by hand.

spec ?= $(error spec is not set)
outdir ?= $(CURDIR)/srpm
pkgdir := $(abspath $(dir $(spec)))

srpm:
	command -v spectool >/dev/null || dnf -y install rpmdevtools rpm-build
	spectool -g -C $(pkgdir) $(spec)
	# Sources that are generated rather than downloaded, such as a Go vendor archive
	if [ -x $(pkgdir)/make-vendor.sh ]; then $(pkgdir)/make-vendor.sh $(pkgdir) $(spec); fi
	rpmbuild -bs \
	  --define "_sourcedir $(pkgdir)" \
	  --define "_srcrpmdir $(outdir)" \
	  --define "dist %{nil}" \
	  $(spec)

.PHONY: srpm
