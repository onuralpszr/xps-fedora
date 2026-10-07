# Intel IPU7 ISYS/PSYS kernel modules as an akmod (RPM Fusion style).
# Modeled on RPM Fusion's intel-ipu6-kmod; patches from omarchy-pkgs
# pkgbuilds/intel-ipu7-camera. akmods signs the built kmods with the
# enrolled /etc/pki/akmods key.
#
# All three modules are built: the out-of-tree PSYS depends on the
# out-of-tree intel-ipu7 bus, so they replace the in-tree staging
# intel-ipu7/intel-ipu7-isys (see the depmod.d override in
# intel-ipu7-camera). Built with BUILD_INTEL_IPU_ACPI=1 like omarchy:
# the isys async-notifier path that binds the sensor via ipu_bridge and
# the Intel CVS bridge is only compiled with CONFIG_INTEL_IPU_ACPI.

%if 0%{?fedora}
%global buildforkernels akmod
%global debug_package %{nil}
%endif

%global drivers_commit a88b19096a738d0708742a78d6540d6d4a3021ff
%global drivers_shortcommit %(c=%{drivers_commit}; echo ${c:0:7})

%global prjname intel-ipu7

Name:           %{prjname}-kmod
Summary:        Kernel module (kmod) for %{prjname}
Version:        1.0.6
Release:        2.dellptl%{?dist}
License:        GPL-2.0-only
URL:            https://github.com/intel/ipu7-drivers

Source0:        https://github.com/intel/ipu7-drivers/archive/%{drivers_commit}/ipu7-drivers-%{drivers_commit}.tar.gz

Patch0:         0004-ipu7-psys-register-device-bus.patch
Patch1:         0005-ipu7-psys-harden-userptr-pinning.patch
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

%prep
%{?kmodtool_check}
kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{prjname} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c
(cd ipu7-drivers-%{drivers_commit}
%patch -P0 -p1 -F0
%patch -P1 -p1 -F0
%patch -P101 -p1
)

for kernel_version in %{?kernel_versions} ; do
  cp -a ipu7-drivers-%{drivers_commit}/ _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions} ; do
  make %{?_smp_mflags} -C ${kernel_version##*___} M=${PWD}/_kmod_build_${kernel_version%%___*} BUILD_INTEL_IPU_ACPI=1 modules
done

%install
for kernel_version in %{?kernel_versions}; do
  dest=%{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
  mkdir -p $dest
  install -m 755 $(find _kmod_build_${kernel_version%%___*} -name '*.ko') $dest/
done
%{?akmod_install}

%changelog
* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-2.dellptl
- Build with BUILD_INTEL_IPU_ACPI=1: without it isys never binds the
  OV08X40 ("no subdevice info provided") and the camera stays black
- Add ipu-acpi, ipu-acpi-pdata, ipu-acpi-common modules
- Hide LT6911 options from the module build (Fedora enables lt6911uxe)

* Mon Oct 05 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-1.dellptl
- Initial akmod for Dell XPS 16 DA16260 (ipu7-drivers a88b190 + omarchy PSYS patches)
