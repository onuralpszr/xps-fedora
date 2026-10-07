# Fedora's llama-cpp (f45, b9840) updated to a current build, with backends
# built as loadable modules (GGML_BACKEND_DL) so each GPU/NPU backend is its
# own subpackage:
#   llama-cpp-vulkan    any Vulkan GPU (Intel Arc, AMD, NVIDIA)
#   llama-cpp-openvino  Intel CPU / GPU / NPU through OpenVINO
#   llama-cpp-hip       AMD ROCm
# The CPU backend is built in all x86-64 variants (SSE4.2 ... AVX-512/AMX)
# and the best one for the running CPU is picked at load time, instead of
# Fedora's baseline-only build.

# For the extra python package gguf that comes with llama-cpp
%global pypi_name gguf
%global pypi_version 0.10.0

# Some optional subpackages
%bcond_with examples
%if %{with examples}
%global build_examples ON
%else
%global build_examples OFF
%endif

%bcond_with test
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

%bcond_with check

Summary:        Port of Facebook's LLaMA model in C/C++
Name:           llama-cpp

# Licensecheck reports
#
# *No copyright* The Unlicense
# ----------------------------
# common/base64.hpp
# common/stb_image.h
# These are public domain
#
# MIT License
# -----------
# LICENSE
# ...
# This is the main license

License:        MIT AND Apache-2.0 AND LicenseRef-Fedora-Public-Domain
Version:        b11460
Release:        1%{?dist}

URL:            https://github.com/ggml-org/llama.cpp
Source0:        %{url}/archive/%{version}.tar.gz#/llama.cpp-%{version}.tar.gz

# aarch64 needs a maintainer
ExclusiveArch:  x86_64 aarch64

%ifarch x86_64
%bcond_without rocm
%else
%bcond_with rocm
%endif
%bcond_without vulkan
%ifarch x86_64
%bcond_without openvino
%else
%bcond_with openvino
%endif

%if %{with rocm}
%global build_hip ON
%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')
%else
%global build_hip OFF
%global toolchain gcc
%endif

%if %{with vulkan}
%global build_vulkan ON
%else
%global build_vulkan OFF
%endif

BuildRequires:  cmake
BuildRequires:  curl
BuildRequires:  git
BuildRequires:  wget
BuildRequires:  xxd
BuildRequires:  langpacks-en
# above are packages in .github/workflows/server.yml
BuildRequires:  libcurl-devel
BuildRequires:  gcc-c++
BuildRequires:  openmpi
BuildRequires:  pthreadpool-devel

%if %{with check}
BuildRequires:  python3-devel
BuildRequires:  python3dist(jinja2)
%endif

%if %{with examples}
BuildRequires:  python3-devel
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(poetry)
%endif

%if %{with rocm}
BuildRequires:  hipblas-devel
BuildRequires:  rocm-comgr-devel
BuildRequires:  rocm-hip-devel
BuildRequires:  rocblas-devel
BuildRequires:  hipblas-devel
BuildRequires:  rocm-runtime-devel
BuildRequires:  rocm-rpm-macros
%endif

%if %{with vulkan}
BuildRequires:  glslc
BuildRequires:  spirv-headers-devel
BuildRequires:  vulkan-headers
BuildRequires:  vulkan-loader-devel
%endif

%if %{with openvino}
BuildRequires:  openvino-devel >= 2026.4
BuildRequires:  opencl-headers
BuildRequires:  pkgconfig(OpenCL)
%endif

Requires:       curl
Recommends:     numactl

%description
The main goal of llama.cpp is to run the LLaMA model using 4-bit
integer quantization on a MacBook

* Plain C/C++ implementation without dependencies
* Apple silicon first-class citizen - optimized via ARM NEON, Accelerate
  and Metal frameworks
* AVX, AVX2 and AVX512 support for x86 architectures
* Mixed F16 / F32 precision
* 2-bit, 3-bit, 4-bit, 5-bit, 6-bit and 8-bit integer quantization support
* CUDA, Metal and OpenCL GPU backend support

The original implementation of llama.cpp was hacked in an evening.
Since then, the project has improved significantly thanks to many
contributions. This project is mainly for educational purposes and
serves as the main playground for developing new features for the
ggml library.

%if %{with vulkan}
%package vulkan
Summary:        Vulkan backend for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Supplements:    %{name}

%description vulkan
GPU acceleration for llama.cpp through Vulkan; works with Intel Arc, AMD and
NVIDIA GPUs that have a Vulkan driver.
%endif

%if %{with openvino}
%package openvino
Summary:        OpenVINO backend for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libopenvino-intel-cpu-plugin
Recommends:     libopenvino-intel-gpu-plugin
Recommends:     libopenvino-intel-npu-plugin

%description openvino
Intel CPU, GPU and NPU acceleration for llama.cpp through OpenVINO. Pick the
device with GGML_OPENVINO_DEVICE=CPU|GPU|NPU; for the NPU use Q4_0 models
and a small context (-c 1024).
%endif

%if %{with rocm}
%package hip
Summary:        AMD ROCm (HIP) backend for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       hipblas
Requires:       rocblas

%description hip
AMD GPU acceleration for llama.cpp through ROCm/HIP.
%endif

%package devel
Summary:        Port of Facebook's LLaMA model in C/C++
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The main goal of llama.cpp is to run the LLaMA model using 4-bit
integer quantization on a MacBook

* Plain C/C++ implementation without dependencies
* Apple silicon first-class citizen - optimized via ARM NEON, Accelerate
  and Metal frameworks
* AVX, AVX2 and AVX512 support for x86 architectures
* Mixed F16 / F32 precision
* 2-bit, 3-bit, 4-bit, 5-bit, 6-bit and 8-bit integer quantization support
* CUDA, Metal and OpenCL GPU backend support

The original implementation of llama.cpp was hacked in an evening.
Since then, the project has improved significantly thanks to many
contributions. This project is mainly for educational purposes and
serves as the main playground for developing new features for the
ggml library.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%if %{with examples}
%package examples
Summary:        Examples for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3dist(numpy)
Requires:       python3dist(torch)
Requires:       python3dist(sentencepiece)

%description examples
%{summary}
%endif

%prep
%autosetup -p1 -n llama.cpp-%{version}

# no android needed
rm -rf examples/llama.android
# git cruft
find . -name '.gitignore' -exec rm -rf {} \;

# Some so version help
sed -i -e 's@WINDOWS_EXPORT_ALL_SYMBOLS ON@WINDOWS_EXPORT_ALL_SYMBOLS ON VERSION ${LLAMA_VERSION_BASE} SOVERSION 0@' tools/batched-bench/CMakeLists.txt
sed -i -e 's@WINDOWS_EXPORT_ALL_SYMBOLS ON@WINDOWS_EXPORT_ALL_SYMBOLS ON VERSION ${LLAMA_VERSION_BASE} SOVERSION 0@' tools/llama-bench/CMakeLists.txt
sed -i -e 's@WINDOWS_EXPORT_ALL_SYMBOLS ON@WINDOWS_EXPORT_ALL_SYMBOLS ON VERSION ${LLAMA_VERSION_BASE} SOVERSION 0@' tools/cli/CMakeLists.txt
sed -i -e 's@WINDOWS_EXPORT_ALL_SYMBOLS ON@WINDOWS_EXPORT_ALL_SYMBOLS ON VERSION ${LLAMA_VERSION_BASE} SOVERSION 0@' tools/completion/CMakeLists.txt
sed -i -e 's@WINDOWS_EXPORT_ALL_SYMBOLS ON@WINDOWS_EXPORT_ALL_SYMBOLS ON VERSION ${LLAMA_VERSION_BASE} SOVERSION 0@' tools/fit-params/CMakeLists.txt
sed -i -e 's@WINDOWS_EXPORT_ALL_SYMBOLS ON@WINDOWS_EXPORT_ALL_SYMBOLS ON VERSION ${LLAMA_VERSION_BASE} SOVERSION 0@' tools/perplexity/CMakeLists.txt
sed -i -e 's@WINDOWS_EXPORT_ALL_SYMBOLS ON@WINDOWS_EXPORT_ALL_SYMBOLS ON VERSION ${LLAMA_VERSION_BASE} SOVERSION 0@' tools/quantize/CMakeLists.txt
sed -i -e 's@WINDOWS_EXPORT_ALL_SYMBOLS ON@WINDOWS_EXPORT_ALL_SYMBOLS ON VERSION ${LLAMA_VERSION_BASE} SOVERSION 0@' tools/server/CMakeLists.txt

%build

%if %{with examples}
cd %{_vpath_srcdir}/gguf-py
%pyproject_wheel
cd -
%endif

%if %{with rocm}
export HIPCC_COMPILE_FLAGS_APPEND="--offload-compress"
%endif

%cmake \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_SKIP_RPATH=ON \
    -DGGML_NATIVE=OFF \
    -DGGML_BACKEND_DL=ON \
    -DGGML_BACKEND_DIR=%{_libdir}/ggml \
%ifarch x86_64
    -DGGML_CPU_ALL_VARIANTS=ON \
%endif
    -DGGML_HIP=%{build_hip} \
    -DGGML_VULKAN=%{build_vulkan} \
    -DGGML_OPENVINO=%{?with_openvino:ON}%{!?with_openvino:OFF} \
    -DAMDGPU_TARGETS="$(echo '%{rocm_gpu_list_default}' | sed -E 's/[;,]?gfx1250//g; s/^[;,]//')" \
    -DLLAMA_BUILD_EXAMPLES=%{build_examples} \
    -DLLAMA_BUILD_TESTS=%{build_test}

%cmake_build

%install
%if %{with examples}
cd %{_vpath_srcdir}/gguf-py
%pyproject_install
cd -
%endif

%cmake_install

rm -rf %{buildroot}%{_libdir}/libggml_shared.*

%if %{with examples}
mkdir -p %{buildroot}%{_datarootdir}/%{name}
cp -r %{_vpath_srcdir}/examples %{buildroot}%{_datarootdir}/%{name}/
cp -r %{_vpath_srcdir}/models %{buildroot}%{_datarootdir}/%{name}/
cp -r %{_vpath_srcdir}/README.md %{buildroot}%{_datarootdir}/%{name}/
rm -rf %{buildroot}%{_datarootdir}/%{name}/examples/llama.android
%endif

%if %{with test}
%if %{with check}
%check
# cpu results
#   14 - test-tokenizers-ggml-vocabs (Failed)              main
# rocm 7.2 gfx1100 results
#   14 - test-tokenizers-ggml-vocabs (Failed)              main
#   36 - test-backend-ops (Subprocess aborted)             main
export LD_LIBRARY_PATH=$PWD/%{_vpath_builddir}/bin
%ctest
%endif
%endif

%files
%license LICENSE
%{_libdir}/libllama.so.*
%{_libdir}/libllama-bench-impl.so.*
%{_libdir}/libllama-batched-bench-impl.so.*
%{_libdir}/libllama-cli-impl.so.*
%{_libdir}/libllama-common.so.*
%{_libdir}/libllama-completion-impl.so.*
%{_libdir}/libllama-fit-params-impl.so.*
%{_libdir}/libllama-perplexity-impl.so.*
%{_libdir}/libllama-quantize-impl.so.*
%{_libdir}/libllama-server-impl.so.*
%{_libdir}/libmtmd.so.*
%{_libdir}/libggml.so.*
%{_libdir}/libggml-base.so.*
%dir %{_libdir}/ggml
%{_libdir}/ggml/libggml-cpu*.so
%{_bindir}/llama
%{_bindir}/llama-batched-bench
%{_bindir}/llama-bench
%{_bindir}/llama-cli
%{_bindir}/llama-completion
%{_bindir}/llama-fit-params
%{_bindir}/llama-gguf-split
%{_bindir}/llama-imatrix
%{_bindir}/llama-mtmd-cli
%{_bindir}/llama-perplexity
%{_bindir}/llama-quantize
%{_bindir}/llama-results
%{_bindir}/llama-server
%{_bindir}/llama-tokenize
%{_bindir}/llama-tts

%if %{with vulkan}
%files vulkan
%{_libdir}/ggml/libggml-vulkan.so
%endif

%if %{with openvino}
%files openvino
%{_libdir}/ggml/libggml-openvino.so
%endif

%if %{with rocm}
%files hip
%{_libdir}/ggml/libggml-hip.so
%endif

%files devel
%dir %{_libdir}/cmake/llama
%dir %{_libdir}/cmake/ggml
%doc README.md
%{_includedir}/gguf.h
%{_includedir}/ggml*.h
%{_includedir}/llama*.h
%{_includedir}/mtmd*.h
%{_libdir}/libllama.so
%{_libdir}/libllama-batched-bench-impl.so
%{_libdir}/libllama-bench-impl.so
%{_libdir}/libllama-cli-impl.so
%{_libdir}/libllama-common.so
%{_libdir}/libllama-completion-impl.so
%{_libdir}/libllama-fit-params-impl.so
%{_libdir}/libllama-perplexity-impl.so
%{_libdir}/libllama-quantize-impl.so
%{_libdir}/libllama-server-impl.so
%{_libdir}/libmtmd.so
%{_libdir}/libggml.so
%{_libdir}/libggml-base.so
%{_libdir}/cmake/llama/*.cmake
%{_libdir}/cmake/ggml/*.cmake
%{_libdir}/pkgconfig/llama.pc

%if %{with test}
%files test
%{_bindir}/test-*
%endif

%if %{with examples}
%files examples
%{_bindir}/convert_hf_to_gguf.py
%{_bindir}/gguf-*
%{_bindir}/llama-*
%{_datarootdir}/%{name}/
%{_libdir}/libllava_shared.so
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}*.dist-info
%{python3_sitelib}/scripts
%endif

%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - b11460-1
- Update to b11460
- Build backends as loadable modules in %{_libdir}/ggml with -vulkan,
  -openvino and -hip subpackages; enable Vulkan and OpenVINO
- Build all x86-64 CPU variants, picked at runtime
- Leave gfx1250 out of the HIP targets (needs newer llama.cpp HIP code)
- Based on Fedora's llama-cpp b9840 packaging
