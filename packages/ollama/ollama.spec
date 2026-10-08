# Ollama 0.40, newer than Fedora's 0.24. Since 0.30 Ollama runs its models
# through llama-server from a pinned llama.cpp that it patches
# (llama/compat), so this builds that llama.cpp the way upstream's
# Dockerfile does and keeps it private in /usr/lib/ollama, next to the
# system llama-cpp:
# - CPU: llama-server, libllama and every x86-64 CPU variant of ggml
# - Vulkan: libggml-vulkan in /usr/lib/ollama/vulkan (Intel Arc and AMD)
# The Go module vendor archive is made at SRPM time by make-vendor.sh.

# llama.cpp release pinned in LLAMA_CPP_VERSION
%global llama_cpp_tag b11351

Name:           ollama
Version:        0.40.1
Release:        1%{?dist}
Summary:        Get up and running with large language models locally

# Ollama is MIT, llama.cpp is MIT; the vendored Go modules (from Fedora's
# go-vendor-tools scan of ollama 0.24) add the rest
License:        MIT AND Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND BSD-3-Clause-HP AND BSL-1.0 AND CC-BY-3.0 AND CC-BY-4.0 AND CC0-1.0 AND ISC AND LicenseRef-Fedora-Public-Domain AND LicenseRef-scancode-protobuf AND NCSA AND NTP AND OpenSSL AND ZPL-2.1 AND Zlib
URL:            https://github.com/ollama/ollama
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/ggml-org/llama.cpp/archive/%{llama_cpp_tag}/llama.cpp-%{llama_cpp_tag}.tar.gz
# Made by make-vendor.sh
Source2:        %{name}-%{version}-vendor.tar.xz
Source10:       ollama.service
Source11:       ollama.sysusers

ExclusiveArch:  x86_64
%global toolchain gcc

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  golang >= 1.26
BuildRequires:  ninja-build
BuildRequires:  openssl-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  glslc
BuildRequires:  spirv-headers-devel
BuildRequires:  vulkan-headers
BuildRequires:  vulkan-loader-devel

# Fedora splits 0.24 into a meta package, -base, -rocm and -vulkan; there is
# no ROCm build here yet
Provides:       %{name}-base = %{version}-%{release}
Provides:       %{name}-base%{?_isa} = %{version}-%{release}
Obsoletes:      %{name}-base < %{version}-%{release}
Obsoletes:      %{name}-rocm < %{version}-%{release}
Recommends:     (%{name}-vulkan%{?_isa} = %{version}-%{release} if vulkan-loader)
Provides:       bundled(llama-cpp) = %{llama_cpp_tag}
Provides:       bundled(ggml)
%{?systemd_requires}

%description
Ollama runs large language models such as Gemma, Qwen, Llama and gpt-oss on
your own machine, with a command line and a local REST API.

%package vulkan
Summary:        Vulkan GPU backend for Ollama
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description vulkan
Runs Ollama models on GPUs through Vulkan, including Intel Arc and AMD GPUs.

%prep
%autosetup -p1
tar -xJf %{SOURCE2}
tar -xzf %{SOURCE1}
mv llama.cpp-%{llama_cpp_tag} llama-cpp-src

%build
# Ollama's build recipes for the CPU and Vulkan payloads (llama/server
# CMakePresets.json), on the unpacked llama.cpp instead of a git fetch;
# configuring applies Ollama's llama/compat patches to it
for preset in cpu vulkan; do
  cmake -S llama/server --preset $preset -G Ninja \
    -DFETCHCONTENT_SOURCE_DIR_LLAMA_CPP=$PWD/llama-cpp-src \
    -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON \
    -DCMAKE_C_FLAGS_RELEASE="%{build_cflags} -DNDEBUG" \
    -DCMAKE_CXX_FLAGS_RELEASE="%{build_cxxflags} -DNDEBUG" \
    -DCMAKE_EXE_LINKER_FLAGS="%{build_ldflags}" \
    -DCMAKE_SHARED_LINKER_FLAGS="%{build_ldflags}" \
    -DCMAKE_MODULE_LINKER_FLAGS="%{build_ldflags}"
  cmake --build build/llama-server-$preset %{?_smp_mflags}
done

export GOTOOLCHAIN=local
export GOFLAGS="-mod=vendor -trimpath -buildmode=pie"
export CGO_CFLAGS="%{build_cflags}"
export CGO_CXXFLAGS="%{build_cxxflags}"
export CGO_LDFLAGS="%{build_ldflags}"
go build -v -ldflags "-B 0x$(head -c20 /dev/urandom | od -An -tx1 | tr -d ' \n') \
  -compressdwarf=false -linkmode=external -extldflags '%{build_ldflags}' \
  -X=github.com/ollama/ollama/version.Version=%{version} \
  -X=github.com/ollama/ollama/server.mode=release" -o ollama .

%install
for preset in cpu vulkan; do
  cmake --install build/llama-server-$preset --component llama-server \
    --prefix %{buildroot}%{_prefix}
done
install -D -m 0755 -p ollama %{buildroot}%{_bindir}/ollama
install -D -m 0644 -p %{SOURCE10} %{buildroot}%{_unitdir}/ollama.service
install -D -m 0644 -p %{SOURCE11} %{buildroot}%{_sysusersdir}/ollama.conf
install -d -m 0755 %{buildroot}%{_sharedstatedir}/ollama

%check
test -x %{buildroot}%{_prefix}/lib/ollama/llama-server
test -e %{buildroot}%{_prefix}/lib/ollama/vulkan/libggml-vulkan.so

%post
%systemd_post ollama.service

%preun
%systemd_preun ollama.service

%postun
%systemd_postun_with_restart ollama.service

%files
%license LICENSE llama-cpp-src/LICENSE vendor/modules.txt
%doc README.md
%{_bindir}/ollama
%dir %{_prefix}/lib/ollama
%{_prefix}/lib/ollama/*
%exclude %{_prefix}/lib/ollama/vulkan
%{_unitdir}/ollama.service
%{_sysusersdir}/ollama.conf
%attr(0755,ollama,ollama) %dir %{_sharedstatedir}/ollama

%files vulkan
%{_prefix}/lib/ollama/vulkan

%changelog
* Thu Oct 08 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 0.40.1-1
- Update to 0.40.1, building Ollama's pinned llama.cpp b11351 with its
  compat patches for the CPU and Vulkan payloads
- Based on Fedora's ollama 0.24.0 packaging
