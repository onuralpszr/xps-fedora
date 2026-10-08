# Fedora's onnx (f45, 1.21.0) updated to 1.22.0, the version OpenVINO 2026.4
# and onnxruntime 1.30 are built against.
#
# 1.22 builds the Python module with scikit-build-core and only supports it
# with a static, hidden-visibility libonnx. Fedora ships a shared libonnx that
# python3-onnx and onnxruntime share, so this keeps the 1.21 layout: one CMake
# build makes the shared libraries and the Python extension, CMake installs
# them, and the dist-info is written here instead of building a wheel.

Name:       onnx
Version:    1.23.2
Release:    1%{?dist}
Summary:    Open standard for machine learning interoperability
License:    Apache-2.0

URL:        https://github.com/onnx/onnx
Source0:    https://github.com/onnx/onnx/archive/v%{version}/%{name}-%{version}.tar.gz
# Shared, versioned libonnx with default visibility; the Python extension
# links it (replaces Fedora's 0001, 0002 and 0005 for 1.21)
Patch:      0001-Fedora-shared-libraries.patch
# Let onnxruntime disable ONNX static schema registration at runtime
Patch:      0002-Add-fixes-for-use-with-onnxruntime.patch

ExcludeArch:    %{ix86}

BuildRequires:  cmake >= 3.26
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  zlib-devel
BuildRequires:  python3-devel
BuildRequires:  python3-nanobind
BuildRequires:  python3-numpy
BuildRequires:  python3-protobuf
BuildRequires:  python3-typing-extensions
BuildRequires:  python3-ml-dtypes
BuildRequires:  python3-pytest
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-static

%global _description %{expand:
%{name} provides an open source format for AI models, both deep learning and
traditional ML. It defines an extensible computation graph model, as well as
definitions of built-in operators and standard data types.}

%description %_description

%package libs
Summary:    Libraries for %{name}

%description libs %_description

%package devel
Summary:    Development files for %{name}
Requires:   %{name}-libs%{?_isa} = %{version}-%{release}

%description devel %_description

%package -n python3-onnx
Summary:    %{summary}
Requires:   %{name}-libs%{?_isa} = %{version}-%{release}
Requires:   python3-numpy
Requires:   python3-protobuf
Requires:   python3-typing-extensions
Requires:   python3-ml-dtypes

%description -n python3-onnx %_description


%prep
%autosetup -p1 -n onnx-%{version}


%build
%cmake -G Ninja \
    -DBUILD_SHARED_LIBS=ON \
    -DONNX_USE_LITE_PROTO=OFF \
    -DONNX_USE_PROTOBUF_SHARED_LIBS=OFF \
    -DONNX_BUILD_PYTHON=ON \
    -DONNX_INSTALL=ON \
    -DONNX_ML=ON \
    -DPython_EXECUTABLE=%{python3} \
    -DPY_SITEARCH=%{python3_sitearch} \
    -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
    -DCMAKE_SKIP_RPATH:BOOL=ON \
    -DONNX_DISABLE_STATIC_REGISTRATION=OFF
%cmake_build


%install
%cmake_install
find %{buildroot}%{_includedir} -type d -empty -delete
install -p onnx/*.proto -t %{buildroot}%{_includedir}/onnx/

# Pure Python part of the package (scikit-build-core would copy the source
# tree); the tests stay out, as in Fedora's 1.21 package
(cd onnx && find . -name '*.py' -o -name '*.pyi' -o -name 'py.typed') \
    | grep -v '^\./test/' \
    | while read f; do install -Dpm0644 onnx/$f %{buildroot}%{python3_sitearch}/onnx/$f; done
# Generated version and protobuf modules from the build tree
cp -p %{__cmake_builddir}/onnx/*.py %{buildroot}%{python3_sitearch}/onnx/ 2>/dev/null || :

d=%{buildroot}%{python3_sitearch}/onnx-%{version}.dist-info
install -d $d
cat > $d/METADATA <<EOF
Metadata-Version: 2.1
Name: onnx
Version: %{version}
Summary: Open Neural Network Exchange
Requires-Dist: numpy>=1.23.2
Requires-Dist: protobuf>=4.25.1
Requires-Dist: typing_extensions>=4.15.0
Requires-Dist: ml_dtypes>=0.5.4
EOF
echo rpm > $d/INSTALLER
cat > $d/entry_points.txt <<EOF
[console_scripts]
backend-test-tools = onnx.backend.test.cmd_tools:main
check-model = onnx.bin.checker:check_model
check-node = onnx.bin.checker:check_node
EOF
install -d %{buildroot}%{_bindir}
for s in backend-test-tools:onnx.backend.test.cmd_tools:main \
         check-model:onnx.bin.checker:check_model \
         check-node:onnx.bin.checker:check_node; do
    name=${s%%%%:*}; rest=${s#*:}; mod=${rest%%%%:*}; fn=${rest#*:}
    printf '#!%{python3}\nimport sys\nfrom %%s import %%s\nsys.exit(%%s())\n' $mod $fn $fn \
        > %{buildroot}%{_bindir}/$name
    chmod 0755 %{buildroot}%{_bindir}/$name
done


%check
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
export PYTHONPATH=%{buildroot}%{python3_sitearch}
(cd / && %{python3} -c "import onnx, onnx.checker, onnx.reference; print(onnx.__version__)")
# Tests that need python-parameterized (not in Fedora) are skipped
# Run the tests against the installed package, not the source tree
cp -a onnx/test %{_builddir}/onnx-tests
cd %{_builddir}
%pytest onnx-tests -p no:cacheprovider \
    $(grep -rlE 'parameterized|from shape_inference_test' onnx-tests --include='*.py' | sed 's/^/--ignore=/') \
    --ignore=onnx-tests/test_backend_reference.py \
    --ignore=onnx-tests/test_backend_test.py


%files libs
%license LICENSE
%doc README.md
%{_libdir}/libonnx.so.%{version}
%{_libdir}/libonnx_proto.so.%{version}

%files devel
%{_libdir}/libonnx.so
%{_libdir}/libonnx_proto.so
%{_libdir}/cmake/ONNX
%{_includedir}/%{name}/

%files -n python3-onnx
%{python3_sitearch}/onnx/
%{python3_sitearch}/onnx-%{version}.dist-info/
%{_bindir}/backend-test-tools
%{_bindir}/check-model
%{_bindir}/check-node


%changelog
* Thu Oct 08 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.23.2-1
- Update to 1.23.2

* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.22.0-1
- Update to 1.22.0
- Port the shared-library setup to 1.22: libonnx keeps default visibility
  and the Python extension links it; install Python files without a wheel
- Based on Fedora's onnx 1.21.0 packaging
