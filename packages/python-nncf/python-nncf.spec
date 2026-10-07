%global pypi_name nncf

Name:           python-%{pypi_name}
Version:        3.4.0
Release:        2%{?dist}
Summary:        Neural Network Compression Framework

License:        Apache-2.0
URL:            https://github.com/openvinotoolkit/nncf
Source:         %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
NNCF provides post-training and training-time algorithms (quantization,
weight compression, pruning) for optimizing neural network inference with
OpenVINO, with support for PyTorch, ONNX and OpenVINO models. It is what
optimum-intel uses to produce INT8/INT4 OpenVINO models.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
# Framework backends are optional and imported on demand
Recommends:     python3-openvino
Suggests:       python3-torch
Suggests:       python3-onnx

%description -n python3-%{pypi_name} %_description


%prep
%autosetup -n %{pypi_name}-%{version}
# Upstream caps dependencies at the versions it has validated; Fedora (and
# rawhide even more so) ships newer ones
sed -i -e 's/"numpy>=1.24.0, <2.5.0"/"numpy>=1.24.0"/' \
       -e 's/"networkx>=2.6, <=3.6.1"/"networkx>=2.6"/' \
       -e 's/"ninja>=1.10.0.post2, <1.14"/"ninja>=1.10.0.post2"/' \
       -e 's/"pydot>=1.4.1, <=4.0.1"/"pydot>=1.4.1"/' pyproject.toml


%generate_buildrequires
# Release version from src/nncf/version.py, no git commit suffix
export NNCF_RELEASE_BUILD=1
%pyproject_buildrequires


%build
export NNCF_RELEASE_BUILD=1
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}


%check
%pyproject_check_import -t


%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md


%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 3.4.0-2
- Drop upper version caps on networkx, ninja and pydot (rawhide)

* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 3.4.0-1
- Initial package
