# Intel IPU7 ISYS/PSYS kernel modules as an akmod (RPM Fusion style).
# Modeled on RPM Fusion's intel-ipu6-kmod; patches from omarchy-pkgs
# pkgbuilds/intel-ipu7-camera. akmods signs the built kmods with the
# enrolled /etc/pki/akmods key.
#
# All three modules are built: the out-of-tree PSYS depends on the
# out-of-tree intel-ipu7 bus, so they replace the in-tree staging
# intel-ipu7/intel-ipu7-isys (see the depmod.d override in
# intel-ipu7-kmod-common). Built with BUILD_INTEL_IPU_ACPI=1 like omarchy:
# the isys async-notifier path that binds the sensor via ipu_bridge and
# the Intel CVS bridge is only compiled with CONFIG_INTEL_IPU_ACPI.

%if 0%{?fedora}
%global buildforkernels akmod
%global debug_package %{nil}
%endif

%global drivers_commit 484d713a0a16635fef5a50975687d5f34fcb535e
%global drivers_shortcommit %(c=%{drivers_commit}; echo ${c:0:7})

%global prjname intel-ipu7

Name:           %{prjname}-kmod
Summary:        Kernel module (kmod) for %{prjname}
Version:        1.0.6
Release:        7.dellptl%{?dist}
License:        GPL-2.0-only
URL:            https://github.com/intel/ipu7-drivers

Source0:        https://github.com/intel/ipu7-drivers/archive/%{drivers_commit}/ipu7-drivers-%{drivers_commit}.tar.gz
Source1:        intel-ipu7-kmod-depmod.conf
Source2:        90-intel-ipu7-kmod-dracut.conf

Patch1:         0005-ipu7-psys-harden-userptr-pinning.patch
# Y10 capture for the HM1092 IR sensor (linux-media 2026-10-10, ported from staging)
Patch2:         0006-ipu7-isys-add-10-bit-greyscale-capture-formats.patch
# Do not oops when the sensor is unbound while streaming (USB IO bridge reset)
Patch3:         0007-ipu7-isys-csi2-handle-a-source-that-is-gone.patch
# Y10 is greyscale, not Bayer: no WARN on every IR crop
Patch4:         0008-ipu7-isys-do-not-treat-Y10-greyscale-as-Bayer.patch
# Fedora enables mainline lt6911uxe; hide LT6911 from the ACPI pdata build
Patch101:       0101-Fedora-hide-LT6911-from-IPU-ACPI-build.patch

BuildRequires:  gcc
BuildRequires:  elfutils-libelf-devel
BuildRequires:  kmodtool

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{prjname} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Out-of-tree Intel IPU7 drivers (intel-ipu7, intel-ipu7-isys and
intel-ipu7-psys) needed by the IPU7 camera HAL on Panther Lake.

# akmods rebuilds this spec with "kernels" set; common comes from the repo
%if %{undefined kernels}
%package -n %{prjname}-kmod-common
Summary:        Module settings for the %{prjname} kmod
BuildArch:      noarch
Requires:       kmod
Requires:       dracut

%description -n %{prjname}-kmod-common
depmod and dracut settings for the out-of-tree Intel IPU7 drivers: the
akmod modules take precedence over the in-tree staging ones, and the IPU7
drivers are kept out of the initramfs, where the probe fails without
ipu7ptl_fw.bin.
%endif

%prep
%{?kmodtool_check}
kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{prjname} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c
(cd ipu7-drivers-%{drivers_commit}
%patch -P1 -p1 -F0
%patch -P2 -p1 -F0
%patch -P3 -p1 -F0
%patch -P4 -p1 -F0
%patch -P101 -p1
)

for kernel_version in %{?kernel_versions} ; do
  cp -a ipu7-drivers-%{drivers_commit}/ _kmod_build_${kernel_version%%___*}
done

%build
# Upstream builds only psys from 6.17 on and leaves the bus and ISYS to
# staging; we need ours (Y10, the CSI-2 fixes), so raise that threshold
for kernel_version in %{?kernel_versions} ; do
  make %{?_smp_mflags} -C ${kernel_version##*___} M=${PWD}/_kmod_build_${kernel_version%%___*} BUILD_INTEL_IPU_ACPI=1 KV_IPU7_ISYS=999.0.0 modules
done

%install
for kernel_version in %{?kernel_versions}; do
  dest=%{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
  mkdir -p $dest
  install -m 755 $(find _kmod_build_${kernel_version%%___*} -name '*.ko') $dest/
done
%{?akmod_install}

%if %{undefined kernels}
install -Dm644 %{SOURCE1} %{buildroot}%{_prefix}/lib/depmod.d/intel-ipu7-kmod.conf
install -Dm644 %{SOURCE2} %{buildroot}%{_prefix}/lib/dracut/dracut.conf.d/90-intel-ipu7-kmod.conf

%post -n %{prjname}-kmod-common
for k in /lib/modules/*/; do depmod -a "$(basename "$k")" 2>/dev/null || :; done
[ $1 -eq 1 ] && touch /run/%{prjname}-kmod-common.dracut || :

%posttrans -n %{prjname}-kmod-common
# on first install, drop the IPU7 drivers from existing initramfs images
if [ -e /run/%{prjname}-kmod-common.dracut ]; then
    rm -f /run/%{prjname}-kmod-common.dracut
    dracut --regenerate-all --force >/dev/null 2>&1 || :
fi

%files -n %{prjname}-kmod-common
%{_prefix}/lib/depmod.d/intel-ipu7-kmod.conf
%{_prefix}/lib/dracut/dracut.conf.d/90-intel-ipu7-kmod.conf
%endif

%changelog
* Mon Nov 02 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-7.dellptl
- Update ipu7-drivers to 484d713 (Intel IPU7 release of 2026-09-26)
- Drop the psys bus registration patch, upstream as 23cf17a
- Rebase the userptr pinning hardening; upstream took part of it
- Keep building our intel-ipu7 bus and ISYS: upstream now builds only
  psys on 6.17 and later

* Mon Nov 02 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-6.dellptl
- Add the intel-ipu7-kmod-common subpackage with the depmod and dracut
  settings: akmod-intel-ipu7 required it, but only intel-ipu7-camera
  provided it, so the kmod could not be installed on its own (#36)

* Mon Oct 19 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-5.dellptl
- Treat Y10 as greyscale, not Bayer: setting the IR sensor crop warned
  in ipu7_isys_convert_bayer_order on every capture

* Fri Oct 16 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-4.dellptl
- Do not oops in CSI-2 stream off when the sensor was unbound while
  streaming (SVP7500 USB IO bridge reset); the camera needed a reboot

* Sat Oct 10 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-3.dellptl
- Add Y10 and Y10P capture formats so the HM1092 IR sensor can be captured

* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-2.dellptl
- Build with BUILD_INTEL_IPU_ACPI=1: without it isys never binds the
  OV08X40 ("no subdevice info provided") and the camera stays black
- Add ipu-acpi, ipu-acpi-pdata, ipu-acpi-common modules
- Hide LT6911 options from the module build (Fedora enables lt6911uxe)

* Mon Oct 05 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-1.dellptl
- Initial akmod for Dell XPS 16 DA16260 (ipu7-drivers a88b190 + omarchy PSYS patches)
