# Fedora's whisper-cpp (1.9.3, libraries only) updated to 1.9.5 and built
# against the system ggml from llama-cpp instead of a bundled copy:
# - Fedora's whisper-cpp and llama-cpp both ship /usr/lib64/libggml*.so.0,
#   so they cannot be installed together; sharing one ggml fixes that
# - every ggml backend llama-cpp builds as a loadable module (Vulkan,
#   OpenVINO, HIP) works for whisper too, picked at run time
# - ships the command line tools (whisper-cli, whisper-server, whisper-stream
#   and friends), which Fedora's package leaves out
# The OpenVINO encoder (WHISPER_OPENVINO) runs the audio encoder on an Intel
# CPU, GPU or NPU through OpenVINO when a converted encoder model is present.

Summary:        Port of OpenAI's Whisper model in C/C++
Name:           whisper-cpp

License:        MIT
# Some exceptions, not distributed:
# Apache-2.0: bindings/java/gradlew*, examples/whisper.android/gradlew*

Version:        1.9.5
Release:        1%{?dist}

URL:            https://github.com/ggml-org/whisper.cpp
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/whisper.cpp-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64 ppc64le
%global toolchain gcc

%ifarch x86_64
%bcond_without openvino
%else
%bcond_with openvino
%endif
# Real-time microphone tools (whisper-stream, whisper-command, talk-llama)
%bcond_without sdl

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  git
# The shared ggml and its cmake config come from llama-cpp-devel
BuildRequires:  llama-cpp-devel >= b11460
%if %{with openvino}
BuildRequires:  openvino-devel >= 2026.4
%endif
%if %{with sdl}
BuildRequires:  SDL2-devel
%endif

# The GPU and NPU backends are loadable ggml modules from llama-cpp
Recommends:     (llama-cpp-vulkan if vulkan-loader)

%description
High-performance inference of OpenAI's Whisper automatic speech recognition
(ASR) model:

* Plain C/C++ implementation without dependencies
* Mixed F16 / F32 precision
* 4-bit, 5-bit and 8-bit integer quantization
* Runs on the CPU, or on a GPU or NPU through the ggml backends from
  llama-cpp (Vulkan, OpenVINO, HIP)
* Voice activity detection (VAD) and Parakeet models

Models are not included. Download one with whisper-download-ggml-model.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       llama-cpp-devel%{?_isa}

%description devel
Header files and cmake configuration for building against libwhisper and
libparakeet.

%prep
%autosetup -p1 -n whisper.cpp-%{version}

%build
%cmake \
    -DWHISPER_BUILD_IS_DEV=OFF \
    -DWHISPER_USE_SYSTEM_GGML=ON \
    -DWHISPER_SDL2=%{?with_sdl:ON}%{!?with_sdl:OFF} \
    -DWHISPER_USE_SYSTEM_LLAMA=%{?with_sdl:ON}%{!?with_sdl:OFF} \
    -DWHISPER_OPENVINO=%{?with_openvino:ON}%{!?with_openvino:OFF} \
    -DWHISPER_BUILD_EXAMPLES=ON \
    -DWHISPER_BUILD_SERVER=ON \
    -DWHISPER_BUILD_TESTS=OFF \
    -DWHISPER_ALL_WARNINGS=OFF \
    -DWHISPER_CURL=OFF
%cmake_build

%install
%cmake_install
install -Dpm755 models/download-ggml-model.sh %{buildroot}%{_bindir}/whisper-download-ggml-model
install -Dpm755 models/download-vad-model.sh %{buildroot}%{_bindir}/whisper-download-vad-model
find %{buildroot} -name 'whisper.pc' -delete

%files
%license LICENSE
%doc README.md
%{_libdir}/libwhisper.so.*
%{_libdir}/libparakeet.so.*
%{_bindir}/whisper-*
%{_bindir}/parakeet-*
%if %{with sdl}
%{_bindir}/whisper-talk-llama
%endif

%files devel
%{_includedir}/whisper.h
%{_includedir}/parakeet.h
%{_libdir}/libwhisper.so
%{_libdir}/libparakeet.so
%{_libdir}/cmake/whisper/
%{_libdir}/cmake/parakeet/
%{_libdir}/pkgconfig/parakeet.pc

%changelog
* Thu Oct 08 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.9.5-1
- Update to 1.9.5
- Build against the system ggml from llama-cpp so both can be installed
- Ship the command line tools and the model download scripts
- Enable the OpenVINO encoder and the SDL2 microphone tools
