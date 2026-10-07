%global pypi_name optimum-intel

Name:           python-%{pypi_name}
Version:        2.2.0
Release:        2%{?dist}
Summary:        Hugging Face Optimum for Intel: OpenVINO and NNCF

License:        Apache-2.0
URL:            https://github.com/huggingface/optimum-intel
Source:         %{pypi_source optimum_intel}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Optimum Intel connects Hugging Face Transformers and Diffusers with OpenVINO:
"optimum-cli export openvino" converts models to OpenVINO IR (with INT8/INT4
weight compression through NNCF) and the OVModel classes run them on Intel
CPUs, GPUs and NPUs.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
# Installs into the optimum namespace; optimum-cli comes from python3-optimum
Requires:       python3-optimum
# Not imported at build time but needed for anything useful
Requires:       python3-openvino-tokenizers
# Exporting models with optimum-cli needs PyTorch; torchvision only for vision models
Recommends:     python3-torch
Suggests:       python3-torchvision

%description -n python3-%{pypi_name} %_description


%prep
%autosetup -n optimum_intel-%{version}
# Fedora's huggingface-hub is newer than the upstream cap; transformers is
# pinned below 5.6 already by python-transformers
sed -i 's/"huggingface-hub>=0.23.2,<1.22"/"huggingface-hub>=0.23.2"/' setup.py


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# python3-optimum owns optimum-cli
rm %{buildroot}%{_bindir}/optimum-cli


%check
# The package imports torch, transformers and openvino at import time; a
# metadata check is all that works without the full stack in the buildroot
test -f %{buildroot}%{python3_sitelib}/optimum/intel/__init__.py


%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{python3_sitelib}/optimum/intel/
%{python3_sitelib}/optimum/exporters/openvino/
%{python3_sitelib}/optimum/commands/register/
%{python3_sitelib}/optimum/commands/export/openvino.py
%{python3_sitelib}/optimum/commands/export/__pycache__/openvino.*
%{python3_sitelib}/optimum_intel-%{version}.dist-info/


%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 2.2.0-2
- Recommend python3-torch for model export

* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 2.2.0-1
- Initial package
