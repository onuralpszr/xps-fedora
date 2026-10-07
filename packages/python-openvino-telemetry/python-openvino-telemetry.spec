%global pypi_name openvino-telemetry

Name:           python-%{pypi_name}
Version:        2025.2.0
Release:        1%{?dist}
Summary:        OpenVINO telemetry library

License:        Apache-2.0
URL:            https://github.com/openvinotoolkit/telemetry
Source:         %{pypi_source openvino_telemetry}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Library used by OpenVINO tools (NNCF, OpenVINO model converter) to send
optional, opt-in usage statistics. Nothing is sent unless the user opts in.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %_description


%prep
%autosetup -n openvino_telemetry-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files -l openvino_telemetry


%check
%pyproject_check_import -t


%files -n python3-%{pypi_name} -f %{pyproject_files}
%doc README.md
%{_bindir}/opt_in_out


%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 2025.2.0-1
- Initial package
