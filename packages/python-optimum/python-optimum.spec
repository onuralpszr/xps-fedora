%global pypi_name optimum

Name:           python-%{pypi_name}
Version:        2.3.0
Release:        1%{?dist}
Summary:        Hugging Face Optimum: hardware-accelerated Transformers

License:        Apache-2.0
URL:            https://github.com/huggingface/optimum
Source:         %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Optimum extends Hugging Face Transformers with tools to export, optimize and
run models on accelerated hardware. Backend-specific support lives in
separate packages such as optimum-intel (OpenVINO).}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %_description


%prep
%autosetup -n %{pypi_name}-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# optimum is a namespace shared with optimum-intel and friends
%pyproject_save_files -l %{pypi_name}


%check
%pyproject_check_import -t


%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md
%{_bindir}/optimum-cli


%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 2.3.0-1
- Initial package
