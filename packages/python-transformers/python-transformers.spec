%global pypi_name transformers

Name:           python-%{pypi_name}
# optimum-intel 2.2 supports transformers < 5.6
Version:        5.5.4
Release:        1%{?dist}
Summary:        State-of-the-art machine learning models for PyTorch

License:        Apache-2.0
URL:            https://github.com/huggingface/transformers
Source:         %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Transformers provides model definitions, pretrained-weight loading and
tokenization for text, vision, audio and multimodal models from the Hugging
Face Hub, for inference and training.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
Recommends:     python3-torch

%description -n python3-%{pypi_name} %_description


%prep
%autosetup -n %{pypi_name}-%{version}
# Fedora's tokenizers 0.23.1 is a bugfix release of the supported 0.23 series
sed -i 's/"tokenizers>=0.22.0,<=0.23.0"/"tokenizers>=0.22.0,<0.24"/' setup.py \
    src/transformers/dependency_versions_table.py


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}


%check
%pyproject_check_import -t


%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md
%{_bindir}/transformers


%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 5.5.4-1
- Initial package
