# Fedora's onnxruntime (f45, 1.26.0) updated to 1.30.0, built against onnx
# 1.22 and OpenVINO 2026.4 (OpenVINO execution provider for Intel CPU, GPU
# and NPU). Fedora's patches, rebased on 1.30 where needed.
#
# Every release renames the library's symbol version (VERS_1.26.0 ->
# VERS_1.30.0), so packages linking libonnxruntime are rebuilt with it.

# Do not check .so files from python or rocm packages
%global __provides_exclude_from ^(%{python3_sitearch}/onnxruntime/.*|%{_libdir}/rocm/lib/.*)$

%if 0%{?fedora} && ! 0%{?flatpak}
%ifarch x86_64
%bcond migraphx 1
# Only for testing purposes, deprecated upstream
%bcond dnnl 0
# Requires updated openVINO with latest onnx and protobuf
%bcond openvino 1
%else
%bcond migraphx 0
%bcond dnnl 0
%bcond openvino 0
%endif
%else
%bcond migraphx 0
%bcond dnnl 0
%bcond openvino 0
%endif

%bcond test 1

# $backend will be evaluated below
%global _vpath_builddir %{_vendor}-%{_target_os}-build-${backend}
%global backends %nil
%global backends %backends cpu
%if %{with migraphx}
%global backends %backends migraphx
%endif
%if %{with dnnl}
%global backends %backends dnnl
%endif
%if %{with openvino}
%global backends %backends openvino
%endif

%global so_version 1

Summary:    A cross-platform inferencing and training accelerator
Name:       onnxruntime
Version:    1.30.0
Release:    1%{?dist}
# onnxruntime and SafeInt are MIT
# onnx is Apache License 2.0
# optional-lite is Boost Software License 1.0
# some protobuf helper files files are BSD (protobuf_function.cmake, pb_helper.*)
License:    MIT AND Apache-2.0 AND BSL-1.0 AND BSD-3-Clause
URL:        https://github.com/microsoft/onnxruntime
Source0:    https://github.com/microsoft/onnxruntime/archive/v%{version}/%{name}-%{version}.tar.gz

# Disable downloading dependencies
Patch:      0001-Disable-download-deps.patch
# Use the system date and boost
Patch:      0002-System-date-and-mp11.patch
# Use the system safeint
Patch:      0003-System-safeint.patch
# Use the system eigen3
Patch:      0004-System-eigen3.patch
# Use the system flatbuffers
Patch:      0005-System-flatbuffers.patch
# Disable gcc -Werror, too strict for downstream packaging
Patch:      0006-Do-not-set-COMPILE_WARNING_AS_ERROR.patch
# Fix deprecated C++20 feature use in migraphx implementation
Patch:      0007-migraphx-Fix-C-20-deprecated-this-capture.patch
# Use the system onednn lib
Patch:      0008-System-dnnl.patch
Patch:      0009-dnnl-Clean-unused-vars.patch
# Use the system openVINO
Patch:      0010-openVINO-runtime-fix.patch
# Trigger onnx static registration fix
Patch:      0011-onnx-static-registration-fix.patch

# armv7hl: https://bugzilla.redhat.com/show_bug.cgi?id=2235328
# i686:    https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    s390x %{arm} %{ix86}

# Force provides declaration since it's not being detected automatically
%ifarch x86_64 aarch64 ppc64 ppc64le s390x riscv64
Provides: libonnxruntime_providers_shared.so()(64bit)
Provides: libonnxruntime_providers_shared.so(VERS_1.0)(64bit)
%else
Provides: libonnxruntime_providers_shared.so
Provides: libonnxruntime_providers_shared.so(VERS_1.0)
%endif

BuildRequires:  cmake >= 3.13
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  onnx-devel = 1.22.0
BuildRequires:  abseil-cpp-devel
BuildRequires:  boost-devel >= 1.66
BuildRequires:  bzip2
%ifnarch ppc64le
BuildRequires:  cpuinfo-devel
%endif
BuildRequires:  date-devel
BuildRequires:  flatbuffers-compiler
BuildRequires:  flatbuffers-devel >= 23.5.26
BuildRequires:  gmock-devel
BuildRequires:  gsl-devel
BuildRequires:  gtest-devel
BuildRequires:  guidelines-support-library-devel
BuildRequires:  json-devel
BuildRequires:  protobuf-devel >= 4
BuildRequires:  protobuf-static >= 4
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  re2-devel >= 20211101
BuildRequires:  safeint-devel
BuildRequires:  zlib-devel
Buildrequires:  eigen3-devel >= 1.34
BuildRequires:  pybind11-devel

%if %{with migraphx}
BuildRequires:  migraphx-devel
BuildRequires:  miopen-devel
BuildRequires:  rocblas-devel
%endif
%if %{with dnnl}
BuildRequires:  onednn-devel
%endif
%if %{with openvino}
BuildRequires:  openvino-devel >= 2026.4
%endif

%description
%{name} is a cross-platform inferencing and training accelerator compatible
with many popular ML/DNN frameworks, including PyTorch, TensorFlow/Keras,
scikit-learn, and more.

%package devel
Summary:    The development part of the %{name} package
Requires:   %{name}%{_isa} = %{version}-%{release}

%description devel
The development part of the %{name} package

%package -n python3-onnxruntime
Summary:    %{summary}

%description -n python3-onnxruntime
Python bindings for the %{name} package

%if %{with test}
%package test
Summary:    The test binaries of the %{name} package
Requires:   %{name}%{_isa} = %{version}-%{release}

%description test
The test binaries of the %{name} package
%endif

%if %{with migraphx}
%package migraphx
Summary:    %{summary}
Conflicts:  %{name}%{_isa} = %{version}-%{release}
Provides:   %{name}%{_isa} = %{version}-%{release}
RemovePathPostfixes: .migraphx

%description migraphx
The migraphx execution provider for the %{name} library

%package -n python3-onnxruntime-migraphx
Summary:    %{summary}
Conflicts:  python3-onnxruntime = %{version}-%{release}
Provides:   python3-onnxruntime = %{version}-%{release}
RemovePathPostfixes: .migraphx:.migraphx.pyc

%description -n python3-onnxruntime-migraphx
The migraphx execution provider for the %{name} python library

%if %{with test}
%package migraphx-test
Summary:    The test binaries of the %{name}-migraphx package
Requires:   %{name}-migraphx%{_isa} = %{version}-%{release}
Conflicts:  %{name}-test%{_isa} = %{version}-%{release}
Provides:   %{name}-test%{_isa} = %{version}-%{release}
RemovePathPostfixes: .migraphx

%description migraphx-test
The test binaries of the %{name}-migraphx package
%endif

%endif

%if %{with dnnl}
%package dnnl
Summary:    %{summary}
Conflicts:  %{name}%{_isa} = %{version}-%{release}
Provides:   %{name}%{_isa} = %{version}-%{release}
RemovePathPostfixes: .dnnl

%description dnnl
The dnnl execution provider for the %{name} library

%package -n python3-onnxruntime-dnnl
Summary:    %{summary}
Conflicts:  python3-onnxruntime = %{version}-%{release}
Provides:   python3-onnxruntime = %{version}-%{release}
RemovePathPostfixes: .dnnl:.dnnl.pyc

%description -n python3-onnxruntime-dnnl
The dnnl execution provider for the %{name} python library

%if %{with test}
%package dnnl-test
Summary:    The test binaries of the %{name}-dnnl package
Requires:   %{name}-dnnl%{_isa} = %{version}-%{release}
Conflicts:  %{name}-test%{_isa} = %{version}-%{release}
Provides:   %{name}-test%{_isa} = %{version}-%{release}
RemovePathPostfixes: .dnnl

%description dnnl-test
The test binaries of the %{name}-dnnl package
%endif

%endif

%if %{with openvino}
%package openvino
Summary:    %{summary}
Conflicts:  %{name}%{_isa} = %{version}-%{release}
Provides:   %{name}%{_isa} = %{version}-%{release}
RemovePathPostfixes: .openvino

%description openvino
The openvino execution provider for the %{name} library

%package -n python3-onnxruntime-openvino
Summary:    %{summary}
Conflicts:  python3-onnxruntime = %{version}-%{release}
Provides:   python3-onnxruntime = %{version}-%{release}
RemovePathPostfixes: .openvino:.openvino.pyc

%description -n python3-onnxruntime-openvino
The openvino execution provider for the %{name} python library

%if %{with test}
%package openvino-test
Summary:    The test binaries of the %{name}-openvino package
Requires:   %{name}-openvino%{_isa} = %{version}-%{release}
Conflicts:  %{name}-test%{_isa} = %{version}-%{release}
Provides:   %{name}-test%{_isa} = %{version}-%{release}
RemovePathPostfixes: .openvino

%description openvino-test
The test binaries of the %{name}-openvino package
%endif

%endif

%package doc
Summary:    Documentation files for the %{name} package

%description doc
Documentation files for the %{name} package

%prep

%autosetup -p1
# Downstream-only: do not pin the version of abseil-cpp; use what we have.
sed -r -i 's/(FIND_PACKAGE_ARGS[[:blank:]]+)[0-9]{8}/\1/' \
    cmake/external/abseil-cpp.cmake
# Remove unnecesary folders
rm -rf onnxruntime/cmake/external/{onnx,libprotobuf-mutator,emsdk}


%build

# Re-compile flatbuffers schemas with the system flatc
%{python3} onnxruntime/core/flatbuffers/schema/compile_schema.py --flatc /usr/bin/flatc
%{python3} onnxruntime/lora/adapter_format/compile_schema.py --flatc /usr/bin/flatc

%global cmake_config \\\
 -DCMAKE_BUILD_TYPE=RelWithDebInfo \\\
 -Donnxruntime_BUILD_BENCHMARKS=OFF \\\
 -Donnxruntime_BUILD_SHARED_LIB=ON \\\
 -Donnxruntime_ENABLE_PYTHON=ON \\\
 -DPYTHON_VERSION=%{python3_version} \\\
 -Donnxruntime_DISABLE_ABSEIL=OFF \\\
 -Donnxruntime_ENABLE_DLPACK=OFF \\\
 -Donnxruntime_USE_FULL_PROTOBUF=ON \\\
 -Donnxruntime_USE_PREINSTALLED_EIGEN=ON \\\
 -Deigen_SOURCE_PATH=/usr/include/eigen3 \\\
 -DProtobuf_BUILD_SHARED_LIBS=OFF \\\
 -S cmake

%ifarch ppc64le
%global cmake_config %cmake_config \\\
 -Donnxruntime_ENABLE_CPUINFO=OFF
%else
%global cmake_config %cmake_config \\\
 -Donnxruntime_ENABLE_CPUINFO=ON
%endif

%if %{with test}
%global cmake_tests \\\
 -Donnxruntime_BUILD_UNIT_TESTS=ON
%else
%global cmake_tests \\\
 -Donnxruntime_BUILD_UNIT_TESTS=OFF
%endif

for backend in %backends; do
    cp -R ./onnxruntime ./onnxruntime.bak
    cp ./requirements.txt ./requirements.txt.bak

    if [ "${backend}" == "cpu" ]; then
        %cmake %cmake_config \
            %cmake_tests
    elif [ "${backend}" == "migraphx" ]; then
        %cmake %cmake_config \
            %cmake_tests \
            -Donnxruntime_USE_MIGRAPHX=ON
    elif [ "${backend}" == "dnnl" ]; then
        %cmake %cmake_config \
            %cmake_tests \
            -Donnxruntime_USE_DNNL=ON
    elif [ "${backend}" == "openvino" ]; then
        %cmake %cmake_config \
            %cmake_tests \
            -Donnxruntime_USE_OPENVINO=ON
    fi

    %cmake_build

    # Build python libs
    cp -R ./%{__cmake_builddir}/onnxruntime/* ./onnxruntime
    cp ./%{__cmake_builddir}/requirements.txt ./requirements.txt

    if [ "${backend}" == "cpu" ]; then
        %pyproject_wheel
    elif [ "${backend}" == "migraphx" ]; then
        %pyproject_wheel -C--global-option=--use_migraphx
    elif [ "${backend}" == "dnnl" ]; then
        cp -p ./%{__cmake_builddir}/libonnxruntime_providers_dnnl.so \
              ./onnxruntime/capi/
        %pyproject_wheel -C--global-option=--use_dnnl
    elif [ "${backend}" == "openvino" ]; then
        %pyproject_wheel -C--global-option=--use_openvino
    fi

    # Store each backend result separately
    mkdir -p dist_onnxruntime_${backend}
    mv %{_pyproject_wheeldir}/*.whl dist_onnxruntime_${backend}/
    mv ./build dist_onnxruntime_${backend}/

    rm -rf ./onnxruntime
    rm -rf ./requirements.txt
    mv ./onnxruntime.bak ./onnxruntime
    mv ./requirements.txt.bak ./requirements.txt
done

%install
mkdir -p %{_builddir}/buildroot_acumulator
for backend in %backends; do
    %cmake_install
    if [ "${backend}" = "cpu" ]; then
        mkdir -p "%{buildroot}/%{_docdir}/"
        cp --preserve=timestamps -r "./docs/" "%{buildroot}/%{_docdir}/%{name}"
    fi

    # Install python libs
    # Retrieve each python wheel
    cp dist_onnxruntime_${backend}/*.whl %{_pyproject_wheeldir}/
    cp -r dist_onnxruntime_${backend}/build ./build

    # Run install process
    %pyproject_install
    %if ! %{with test}
        rm -rf %{buildroot}%{_bindir}
    %endif
    

    if [ "${backend}" = "cpu" ]; then
        # List installed files and copy result
        %pyproject_save_files onnxruntime
        cp %{pyproject_files} %{_builddir}/files_${backend}

    else
        # List installed files and copy result
        %pyproject_save_files onnxruntime 'onnxruntime*'
        cp %{pyproject_files} %{_builddir}/files_${backend}

        # Add postfix to files in onnxruntime directory from specific backend
        sed -i '/^%dir/! { /\.dist-info/! s/$/.'"${backend}"'/}' %{_builddir}/files_${backend}
        find %{buildroot}%{python3_sitearch}/onnxruntime/ -type f -exec bash -c 'mv "${0}" "${0}.'"${backend}"'"' {} \;

        # Make sure that even if they have a postfix, to keep the extension of .pyc files
        # so that they are properly processed on the check-buildroot step.
        sed -i 's/.pyc.'"${backend}"'$/.pyc.'"${backend}"'.pyc/' %{_builddir}/files_${backend}
        find %{buildroot}%{python3_sitearch}/onnxruntime/ -type f -iname "*.pyc.${backend}" -exec bash -c 'mv "${0}" "${0}.pyc"' {} \;

        # Rename other installed files
        mv  %{buildroot}%{_libdir}/libonnxruntime.so.%{version} \
            %{buildroot}%{_libdir}/libonnxruntime.so.%{version}.${backend}
        mv  %{buildroot}%{_libdir}/libonnxruntime_providers_shared.so \
            %{buildroot}%{_libdir}/libonnxruntime_providers_shared.so.${backend}

        %if %{with test}
            mv  %{buildroot}%{_bindir}/onnx_test_runner \
                %{buildroot}%{_bindir}/onnx_test_runner.${backend}
            mv  %{buildroot}%{_bindir}/onnxruntime_test \
                %{buildroot}%{_bindir}/onnxruntime_test.${backend}
        %endif
    fi

    # Remove this file on each loop so that pyproject_save_files works properly 
    rm -f %{_pyproject_record}
    # Store results so that they don't get overwritten in the loop
    cp -a %{buildroot}/* %{_builddir}/buildroot_acumulator/
    rm -rf %{buildroot}/*

    # Reset environment
    rm -rf %{_pyproject_wheeldir}/*
    rm -rf ./build
done

# Restore results
mkdir -p %{buildroot}
cp -a %{_builddir}/buildroot_acumulator/* %{buildroot}
rm -rf %{_builddir}/buildroot_acumulator

%if %{with test}
%check
export GTEST_FILTER=" \
    -CContribOpTest.StringNormalizerSensitiveFilterOutNoCase \
    -CContribOpTest.StringNormalizerSensitiveFilterOutLower \
    -CContribOpTest.StringNormalizerSensitiveFilterOutUpper \
    -CContribOpTest.StringNormalizerSensitiveFilterOutUpperWithLocale \
    -CContribOpTest.StringNormalizerInsensitiveFilterOutUpperWithLocale \
    -CContribOpTest.StringNormalizerSensitiveFilterOutUpperEmptyCase \
    -CContribOpTest.StringNormalizerSensitiveFilterOutUpperSameOutput \
    -CRandom.MultinomialGoodCase \
    -CRandom.MultinomialDefaultDType \
    -CSamplingTest.Gpt2Sampling_CPU "

%if %{with test}
for backend in %backends; do
    %ctest
done
%endif

%endif

%files
%license LICENSE ThirdPartyNotices.txt
%{_libdir}/libonnxruntime.so.%{so_version}
%{_libdir}/libonnxruntime.so.%{version}
%{_libdir}/libonnxruntime_providers_shared.so

%files devel
%dir %{_includedir}/onnxruntime/
%dir %{_libdir}/cmake/onnxruntime/
%{_includedir}/onnxruntime/*
%{_libdir}/cmake/onnxruntime/*
%{_libdir}/libonnxruntime.so
%{_libdir}/pkgconfig/libonnxruntime.pc

%files -n python3-onnxruntime -f %{_builddir}/files_cpu

%if %{with test}
%files test
%{_bindir}/onnx_test_runner
%{_bindir}/onnxruntime_test
%endif

%if %{with migraphx}
%files migraphx
%license LICENSE ThirdPartyNotices.txt
%{_libdir}/libonnxruntime.so.%{so_version}
%{_libdir}/libonnxruntime.so.%{version}.migraphx
%{_libdir}/libonnxruntime_providers_shared.so.migraphx
%{_libdir}/libonnxruntime_providers_migraphx.so

%files -n python3-onnxruntime-migraphx -f %{_builddir}/files_migraphx

%if %{with test}
%files migraphx-test
%{_bindir}/onnx_test_runner.migraphx
%{_bindir}/onnxruntime_test.migraphx
%endif
%endif

%if %{with dnnl}
%files dnnl
%license LICENSE ThirdPartyNotices.txt
%{_libdir}/libonnxruntime.so.%{so_version}
%{_libdir}/libonnxruntime.so.%{version}.dnnl
%{_libdir}/libonnxruntime_providers_shared.so.dnnl
%{_libdir}/libonnxruntime_providers_dnnl.so

%files -n python3-onnxruntime-dnnl -f %{_builddir}/files_dnnl

%if %{with test}
%files dnnl-test
%{_bindir}/onnx_test_runner.dnnl
%{_bindir}/onnxruntime_test.dnnl
%endif
%endif

%if %{with openvino}
%files openvino
%license LICENSE ThirdPartyNotices.txt
%{_libdir}/libonnxruntime.so.%{so_version}
%{_libdir}/libonnxruntime.so.%{version}.openvino
%{_libdir}/libonnxruntime_providers_shared.so.openvino
%{_libdir}/libonnxruntime_providers_openvino.so

%files -n python3-onnxruntime-openvino -f %{_builddir}/files_openvino

%if %{with test}
%files openvino-test
%{_bindir}/onnx_test_runner.openvino
%{_bindir}/onnxruntime_test.openvino
%endif
%endif

%files doc
%{_docdir}/%{name}

%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.30.0-1
- Update to 1.30.0
- Build against onnx 1.22.0 and OpenVINO 2026.4.1
- Rebase Disable-download-deps and System-date-and-mp11 patches on 1.30
- Based on Fedora's onnxruntime 1.26.0 packaging
