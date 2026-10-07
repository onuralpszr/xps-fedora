# Fedora's intel-npu-driver (f45, 1.35.0) updated to 1.38.0, plus an
# intel-npu-compiler subpackage with Intel's prebuilt NPU compiler.
#
# Fedora builds with ENABLE_NPU_COMPILER_BUILD=OFF, so OpenVINO cannot compile
# models for the NPU ("Unsupported configuration key: NPU_MAX_TILES" with
# OpenVINO 2026.4). Building the compiler from source needs OpenVINO + an LLVM
# fork; Intel ships it prebuilt (Apache-2.0) in each driver release, matched to
# that driver version. Since 1.38 the driver dlopens
# libopenvino_intel_npu_compiler_loader.so (1.32 looked for
# libnpu_driver_compiler.so), so driver and compiler have to move together.
#
# Release 0.x so Fedora's own 1.38.0-1 supersedes the driver once it lands.

%global ext_commit      f9ad3bf89c2418d714aef2e6b96a5aafb12a1971
%global elf_commit      d325f45f2cb405b5fa2ff17a30de9469f1641b73
%global intel_build     20260910-34487311128

Name:		intel-npu-driver
Version:	1.38.0
Release:	0.1.dellptl%{?dist}
Summary:	Intel Neural Processing Unit Driver

License:	MIT AND Apache-2.0
URL:		https://github.com/intel/linux-npu-driver
Source0:	%url/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:	https://github.com/intel/level-zero-npu-extensions/archive/%{ext_commit}/level-zero-npu-extensions-%{sub %{ext_commit} 1 7}.tar.gz
Source2:	https://github.com/openvinotoolkit/npu_compiler_elf/archive/%{elf_commit}/npu_compiler_elf-%{sub %{elf_commit} 1 7}.tar.gz
# Prebuilt compiler, from the same release as Source0
Source3:	%url/releases/download/v%{version}/linux-npu-driver-v%{version}.%{intel_build}-ubuntu2604.tar.gz

# Fedora's oneapi-level-zero 1.33 headers have DDI entries 1.38 doesn't set
# yet (-Werror=missing-field-initializers); replaces Fedora's
# add-initializer-umd-level_zero_driver-ze_device.patch, mostly upstream now
Patch0:		0001-umd-initialize-DDI-entries-from-level-zero-1.33.patch

ExclusiveArch:	x86_64

BuildRequires:	cmake
BuildRequires:	gcc-c++
BuildRequires:	glibc-devel
BuildRequires:	gmock-devel
BuildRequires:	gtest-devel
BuildRequires:	libudev-devel
BuildRequires:	oneapi-level-zero-devel
BuildRequires:	openssl-devel
BuildRequires:	yaml-cpp-devel
BuildRequires:	binutils
# openvino-npu_compiler_elf
Provides:	bundled(openvino-npu_compiler_elf)
# level-zero-npu-extensions
Provides:	bundled(level-zero-npu-extensions)
Requires:	oneapi-level-zero
Recommends:	intel-npu-compiler%{?_isa} = %{version}-%{release}

%description
Intel NPU device is an AI inference accelerator integrated with Intel client
CPUs, starting from Intel Core Ultra generation of CPUs (formerly known as
Meteor Lake). It enables energy-efficient execution of artificial neural
network tasks.

%package -n intel-npu-compiler
Summary:	Intel NPU compiler (prebuilt) for the NPU Level Zero driver
License:	Apache-2.0
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description -n intel-npu-compiler
The NPU compiler the Level Zero driver loads to compile OpenVINO models for
the NPU (libopenvino_intel_npu_compiler and its loader). Prebuilt by Intel
and taken unmodified from the linux-npu-driver v%{version} release.

%package test
Summary:	Test files for %{name}
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description test
The %{name}-test package contains kernel-mode (kmd) and user-mode (umd)
parts of the %{name}.

%package -n intel-npu-smi
Summary:	Utility tool to track NPU telemetry data

%description -n intel-npu-smi
The intel-npu-smi package utility tool for tracking NPU telemetry power reporting

%prep
%autosetup -N -n linux-npu-driver-%{version}

# thirdparty deps
rm -rf third_party/googletest \
  third_party/level-zero-npu-extensions \
  third_party/npu_compiler_elf \
  third_party/yaml-cpp
tar xf %{SOURCE1}
mv level-zero-npu-extensions-* third_party/level-zero-npu-extensions
tar xf %{SOURCE2}
mv npu_compiler_elf-* third_party/npu_compiler_elf

%autopatch -p1

# Prebuilt compiler out of Intel's .deb
mkdir -p prebuilt && pushd prebuilt
tar xf %{SOURCE3}
ar x intel-driver-compiler-npu_*.deb
tar xf data.tar.*
popd

%build
%cmake \
	-DCMAKE_BUILD_TYPE=Release \
	-DUSE_SYSTEM_LIBRARIES=ON \
	-DENABLE_NPU_PERFETTO_BUILD=ON \
	-DENABLE_TOOLS_BUILD=ON \
	-DENABLE_NPU_COMPILER_BUILD=OFF
%cmake_build

%install
%cmake_install

# remove the unversioned so file
rm -vf %{buildroot}%{_libdir}/libze_intel_npu.so

# install NPU shared tests
install -d %{buildroot}%{_bindir}
install -m 0755 redhat-linux-build/bin/*npu_*tests %{buildroot}%{_bindir}/

install -m 0755 prebuilt/usr/lib/x86_64-linux-gnu/libopenvino_intel_npu_compiler.so \
	prebuilt/usr/lib/x86_64-linux-gnu/libopenvino_intel_npu_compiler_loader.so \
	%{buildroot}%{_libdir}/

# Stage source trees inside the cmake build dir so debugedit/cpio can find
# files for /usr/src/debug/. DWARF records paths as "redhat-linux-build/<sub>/..."
# but the real sources live at "<sub>/..." in the unpacked tarball.
mkdir -p redhat-linux-build/third_party/npu_compiler_elf
cp -a third_party/npu_compiler_elf/. redhat-linux-build/third_party/npu_compiler_elf/
cp -a umd/.                          redhat-linux-build/umd/
cp -a validation/.                   redhat-linux-build/validation/
mkdir -p redhat-linux-build/third_party/perfetto/sdk
cp -a third_party/perfetto/sdk/.     redhat-linux-build/third_party/perfetto/sdk/
cp -a tools/intel-npu-smi/.          redhat-linux-build/tools/intel-npu-smi/

%files
%license LICENSE.md
%doc README.md
%{_libdir}/libze_intel_npu.so.1
%{_libdir}/libze_intel_npu.so.%{version}

%files -n intel-npu-compiler
%license LICENSE.md
%{_libdir}/libopenvino_intel_npu_compiler.so
%{_libdir}/libopenvino_intel_npu_compiler_loader.so

%files test
%{_bindir}/npu-kmd-test
%{_bindir}/npu-umd-test
%{_bindir}/*npu_*tests

%files -n intel-npu-smi
%{_bindir}/intel-npu-smi

%changelog
* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.38.0-0.1.dellptl
- Update to 1.38.0 (npu_compiler_elf d325f45)
- Add intel-npu-compiler subpackage with Intel's prebuilt NPU compiler so
  OpenVINO can compile for the NPU (Panther Lake tested with OpenVINO 2026.4)
- Replace Fedora's DDI initializer patch with one for 1.38 + level-zero 1.33
- Based on Fedora f45 intel-npu-driver-1.35.0
