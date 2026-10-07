# Desktop tools for Dell XPS on Intel Panther Lake (Fedora KDE)

Name:           xps-ptl-tools
Version:        0.5
Release:        1%{?dist}
Summary:        Desktop tools for Dell XPS on Intel Panther Lake
License:        MIT
URL:            https://github.com/omacom-io/omarchy-pkgs
BuildArch:      noarch

Source0:        xps-ptl-autobrightness
Source1:        xps-ptl-autobrightness.service
Source3:        autobrightness.conf
Source4:        README.md
Source5:        plasmoid

BuildRequires:  systemd-rpm-macros
Requires:       python3
Requires:       python3-dbus
Requires:       python3-gobject
Requires:       iio-sensor-proxy
Requires:       hicolor-icon-theme
# the widget uses org.kde.plasma.workspace.dbus
Recommends:     plasma-workspace >= 6.0

%description
Ambient-light auto-brightness for KDE Plasma (user service reading
iio-sensor-proxy and driving org.kde.ScreenBrightness, with a learned
user preference), and an "Auto Brightness" Plasma widget to see and
control it.

%prep

%build

%install
install -Dm755 %{SOURCE0} %{buildroot}%{_bindir}/xps-ptl-autobrightness
install -Dm644 %{SOURCE1} %{buildroot}%{_userunitdir}/xps-ptl-autobrightness.service
install -Dm644 %{SOURCE3} %{buildroot}%{_sysconfdir}/xps-ptl/autobrightness.conf
install -Dm644 %{SOURCE4} %{buildroot}%{_docdir}/%{name}/README.md
install -d %{buildroot}%{_datadir}/plasma/plasmoids
cp -r %{SOURCE5}/org.xpsptl.autobrightness %{buildroot}%{_datadir}/plasma/plasmoids/
# colour icon for the widget list and the tooltip
install -Dm644 %{SOURCE5}/org.xpsptl.autobrightness/contents/icons/autobrightness.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/xps-ptl-autobrightness.svg

%post
%systemd_user_post xps-ptl-autobrightness.service

%preun
%systemd_user_preun xps-ptl-autobrightness.service

%postun
%systemd_user_postun_with_restart xps-ptl-autobrightness.service

%files
%{_bindir}/xps-ptl-autobrightness
%{_userunitdir}/xps-ptl-autobrightness.service
%dir %{_sysconfdir}/xps-ptl
%config(noreplace) %{_sysconfdir}/xps-ptl/autobrightness.conf
%{_docdir}/%{name}/README.md
%{_datadir}/plasma/plasmoids/org.xpsptl.autobrightness/
%{_datadir}/icons/hicolor/scalable/apps/xps-ptl-autobrightness.svg

%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 0.5-1
- Spike filter: the ALS reports bursts of impossible values (up to ~115 000 lx
  for 0.5-1.5 s in a dark room); sample every 0.5 s, drop > max_lux, use the
  30th percentile of a 6 s window before smoothing

* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 0.4-1
- Widget: give the popup its content height (it collapsed to the header
  in the panel)

* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 0.3-1
- Don't enable the user service globally on install (no preset); each user
  enables it with systemctl --user or the widget's Start button

* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 0.2-1
- Widget: own icons (screen + ambient light sensor), ambient light and
  screen cards, preference slider (SetOffset), status line
- Service: SetOffset(d), Target property; fix detection of an already
  running service in the widget

* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 0.1-1
- xps-ptl-autobrightness: ambient-light auto-brightness for KDE Plasma
- Auto Brightness Plasma widget
