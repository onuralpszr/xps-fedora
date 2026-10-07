# OpenVINO GenAI and OpenVINO Tokenizers, built together the way upstream
# releases them: GenAI builds the tokenizers extension from its
# thirdparty/openvino_tokenizers submodule and both must match the OpenVINO
# version exactly.
#
# Everything CMake would download (FetchContent) is listed as a Source and
# handed over with FETCHCONTENT_SOURCE_DIR_*, so the build works offline.

%global ov_version          2026.4.1
# cmake component of the Python module, e.g. pygenai_3_15
%global pygenai_component   pygenai_%(echo %{python3_version} | tr . _)

%global sentencepiece_ver   0.2.1
%global pcre2_ver           10.48
%global json_ver            3.11.3
%global minja_commit        3e4c61c616eda133cfb1e440fc7a14bf1729bbee
%global safetensors_commit  974a85d7dfd6e010558353226638bb26d6b9d756
%global gguf_tools_commit   bac796ada809ac293e685db59b075971181cb008
%global xgrammar_ver        0.1.31
%global dlpack_commit       bbd2f4d32427e548797929af08cfe2a9cbb3cf12
%global pybind11_ver        3.0.1

Name:           openvino-genai
Version:        2026.4.1.0
Release:        1%{?dist}
Summary:        Generative AI pipelines for OpenVINO

# GenAI, Tokenizers: Apache-2.0
# sentencepiece: Apache-2.0; pcre2: BSD-3-Clause; nlohmann-json, minja,
# safetensors.h, gguf-tools: MIT; xgrammar: Apache-2.0; dlpack: Apache-2.0;
# pybind11: BSD-3-Clause
License:        Apache-2.0 AND BSD-3-Clause AND MIT
URL:            https://github.com/openvinotoolkit/openvino.genai

Source0:        %{url}/archive/%{version}/openvino.genai-%{version}.tar.gz
Source1:        https://github.com/openvinotoolkit/openvino_tokenizers/archive/%{version}/openvino_tokenizers-%{version}.tar.gz
Source2:        https://github.com/google/sentencepiece/releases/download/v%{sentencepiece_ver}/sentencepiece-%{sentencepiece_ver}.tar.gz
Source3:        https://github.com/PCRE2Project/pcre2/releases/download/pcre2-%{pcre2_ver}/pcre2-%{pcre2_ver}.zip
Source4:        https://github.com/nlohmann/json/archive/v%{json_ver}/json-%{json_ver}.tar.gz
Source5:        https://github.com/google/minja/archive/%{minja_commit}/minja-%{sub %{minja_commit} 1 7}.tar.gz
Source6:        https://github.com/hsnyder/safetensors.h/archive/%{safetensors_commit}/safetensors.h-%{sub %{safetensors_commit} 1 7}.tar.gz
Source7:        https://github.com/Lourdle/gguf-tools/archive/%{gguf_tools_commit}/gguf-tools-%{sub %{gguf_tools_commit} 1 7}.tar.gz
Source8:        https://github.com/mlc-ai/xgrammar/archive/v%{xgrammar_ver}/xgrammar-%{xgrammar_ver}.tar.gz
Source9:        https://github.com/dmlc/dlpack/archive/%{dlpack_commit}/dlpack-%{sub %{dlpack_commit} 1 7}.tar.gz
Source10:       https://github.com/pybind/pybind11/archive/v%{pybind11_ver}/pybind11-%{pybind11_ver}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  unzip
BuildRequires:  openvino-devel >= %{ov_version}
BuildRequires:  python3-devel

Requires:       openvino-tokenizers%{?_isa} = %{version}-%{release}

%global _description %{expand:
OpenVINO GenAI runs generative models (LLMs, VLMs, Whisper, image generation,
text-to-speech) on Intel CPUs, GPUs and NPUs with OpenVINO, with a C++, C and
Python API.}

%description %_description


%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       openvino-devel >= %{ov_version}

%description devel %_description
.
Headers, CMake config and libraries for building against OpenVINO GenAI.


%package -n python3-%{name}
Summary:        Python API for OpenVINO GenAI
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-openvino >= %{ov_version}
Requires:       python3-openvino-tokenizers = %{version}-%{release}

%description -n python3-%{name} %_description
.
This package provides the openvino_genai Python module.


%package -n openvino-tokenizers
Summary:        OpenVINO extension with tokenizer and detokenizer operations
License:        Apache-2.0 AND BSD-3-Clause
Provides:       bundled(sentencepiece) = %{sentencepiece_ver}
Provides:       bundled(pcre2) = %{pcre2_ver}
Requires:       openvino%{?_isa} >= %{ov_version}

%description -n openvino-tokenizers
OpenVINO Tokenizers adds tokenizer and detokenizer operations to OpenVINO, so
that text pre- and post-processing runs inside the model (and on the same
device).


%package -n python3-openvino-tokenizers
Summary:        Convert Hugging Face tokenizers to OpenVINO models
License:        Apache-2.0
BuildArch:      noarch
Requires:       openvino-tokenizers = %{version}-%{release}
Requires:       python3-openvino >= %{ov_version}

%description -n python3-openvino-tokenizers
Python module and convert_tokenizer tool that turn Hugging Face tokenizers
into OpenVINO models using the openvino-tokenizers extension.


%prep
%autosetup -n openvino.genai-%{version}

tar xf %{SOURCE1}
rmdir thirdparty/openvino_tokenizers
mv openvino_tokenizers-%{version} thirdparty/openvino_tokenizers

mkdir -p deps
tar xf %{SOURCE2} -C deps
unzip -q %{SOURCE3} -d deps
tar xf %{SOURCE4} -C deps
tar xf %{SOURCE5} -C deps
tar xf %{SOURCE6} -C deps
tar xf %{SOURCE7} -C deps
tar xf %{SOURCE8} -C deps
tar xf %{SOURCE9} -C deps
rmdir deps/xgrammar-%{xgrammar_ver}/3rdparty/dlpack
mv deps/dlpack-%{dlpack_commit} deps/xgrammar-%{xgrammar_ver}/3rdparty/dlpack
tar xf %{SOURCE10} -C deps


%build
# Upstream is written for C++17 (GCC 16 defaults to C++20, which changes
# aggregate and u8 literal rules). xgrammar builds with -Werror and GCC 16
# reports a false -Warray-bounds in it.
export CXXFLAGS="%{optflags} -Wno-error"
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_INSTALL_INCLUDEDIR=include \
    -DCMAKE_INSTALL_BINDIR=bin \
    -DCMAKE_COMPILE_WARNING_AS_ERROR=OFF \
    -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
    -DFETCHCONTENT_SOURCE_DIR_SENTENCEPIECE=$PWD/deps/sentencepiece-%{sentencepiece_ver} \
    -DFETCHCONTENT_SOURCE_DIR_PCRE2=$PWD/deps/pcre2-%{pcre2_ver} \
    -DFETCHCONTENT_SOURCE_DIR_NLOHMANN_JSON=$PWD/deps/json-%{json_ver} \
    -DFETCHCONTENT_SOURCE_DIR_MINJA=$PWD/deps/minja-%{minja_commit} \
    -DFETCHCONTENT_SOURCE_DIR_SAFETENSORS.H=$PWD/deps/safetensors.h-%{safetensors_commit} \
    -DFETCHCONTENT_SOURCE_DIR_GGUFLIB=$PWD/deps/gguf-tools-%{gguf_tools_commit} \
    -DFETCHCONTENT_SOURCE_DIR_XGRAMMAR=$PWD/deps/xgrammar-%{xgrammar_ver} \
    -DFETCHCONTENT_SOURCE_DIR_PYBIND11=$PWD/deps/pybind11-%{pybind11_ver} \
    -DXGRAMMAR_ENABLE_CPPTRACE=OFF \
    -DENABLE_PYTHON=ON \
    -DPython3_EXECUTABLE=%{python3} \
    -DENABLE_JS=OFF \
    -DENABLE_SAMPLES=OFF \
    -DENABLE_TESTS=OFF \
    -DENABLE_TOOLS=OFF \
    -DBUILD_TOKENIZERS=ON
%cmake_build


%install
# Upstream installs the Intel archive layout (runtime/lib/intel64, python/);
# stage it and move everything to the Fedora locations.
stage=$PWD/stage
for c in core_genai core_genai_dev core_c_genai core_c_genai_dev \
         openvino_tokenizers %{pygenai_component}; do
    DESTDIR= cmake --install %{__cmake_builddir} --prefix $stage --component $c
done

install -d %{buildroot}%{_libdir} %{buildroot}%{_includedir} \
           %{buildroot}%{_libdir}/cmake/OpenVINOGenAI \
           %{buildroot}%{python3_sitearch} %{buildroot}%{python3_sitelib}
cp -a $stage/runtime/lib/intel64/*.so* %{buildroot}%{_libdir}/
cp -a $stage/runtime/include/. %{buildroot}%{_includedir}/
cp -a $stage/runtime/cmake/. %{buildroot}%{_libdir}/cmake/OpenVINOGenAI/
# The exported targets point at the archive layout; point them at /usr
sed -i -e 's|${_IMPORT_PREFIX}/runtime/lib/intel64|%{_libdir}|g' \
       -e 's|${_IMPORT_PREFIX}/runtime/include|%{_includedir}|g' \
       %{buildroot}%{_libdir}/cmake/OpenVINOGenAI/OpenVINOGenAITargets*.cmake
cp -a $stage/python/openvino_genai %{buildroot}%{python3_sitearch}/

# Python openvino_tokenizers is pure Python; it loads the extension from the
# library path when it is not bundled inside the package
cp -a thirdparty/openvino_tokenizers/python/openvino_tokenizers %{buildroot}%{python3_sitelib}/
cp -p %{__cmake_builddir}/openvino_tokenizers/python/__version__.py \
      %{buildroot}%{python3_sitelib}/openvino_tokenizers/__version__.py
install -d %{buildroot}%{_bindir}
make_script() {
    printf '#!%{python3}\nimport sys\nfrom %%s import %%s\nsys.exit(%%s())\n' "$2" "$3" "$3" \
        > %{buildroot}%{_bindir}/$1
    chmod 0755 %{buildroot}%{_bindir}/$1
}
make_script openvino_tokenizers openvino_tokenizers.cli_tools.main main
make_script convert_tokenizer openvino_tokenizers.cli_tools.convert_tokenizer convert_hf_tokenizer

# dist-info so both modules are visible to pip and to RPM's python3dist()
write_dist_info() {
    d=$1/$2-%{version}.dist-info; shift 2
    install -d $d
    { echo "Metadata-Version: 2.1"; echo "Name: $1"; echo "Version: %{version}"
      shift; for r in "$@"; do echo "Requires-Dist: $r"; done; } > $d/METADATA
    echo rpm > $d/INSTALLER
}
write_dist_info %{buildroot}%{python3_sitearch} openvino_genai openvino-genai \
    "openvino-tokenizers~=%{version}"
write_dist_info %{buildroot}%{python3_sitelib} openvino_tokenizers openvino-tokenizers \
    "openvino~=%{ov_version}"


%check
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
export PYTHONPATH=%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}
%{python3} -c "import openvino_tokenizers, openvino_genai; print(openvino_genai.__version__)"


%files
%license LICENSE
%doc README.md
%{_libdir}/libopenvino_genai.so.*
%{_libdir}/libopenvino_genai_c.so.*

%files devel
%{_includedir}/openvino/genai/
%{_libdir}/libopenvino_genai.so
%{_libdir}/libopenvino_genai_c.so
%{_libdir}/cmake/OpenVINOGenAI/

%files -n python3-%{name}
%{python3_sitearch}/openvino_genai/
%{python3_sitearch}/openvino_genai-%{version}.dist-info/

%files -n openvino-tokenizers
%license thirdparty/openvino_tokenizers/LICENSE
%{_libdir}/libopenvino_tokenizers.so

%files -n python3-openvino-tokenizers
%doc thirdparty/openvino_tokenizers/README.md
%{_bindir}/convert_tokenizer
%{_bindir}/openvino_tokenizers
%{python3_sitelib}/openvino_tokenizers/
%{python3_sitelib}/openvino_tokenizers-%{version}.dist-info/


%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 2026.4.1.0-1
- Initial package
- Build as C++17 for GCC 16
