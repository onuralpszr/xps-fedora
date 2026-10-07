# System configuration for Dell XPS 14/16 (Panther Lake) on Fedora:
# - thermald: fix the boot race that leaves adaptive-only Panther Lake
#   without thermald
# - kernel-install hook: sign *.dellptl* kernels with the akmods MOK key so
#   they boot with Secure Boot on
# - xe: PSR1 instead of PSR2 selective fetch (glitches on the LG OLED)
# - power profiles: KDE's slider drives Dell thermal modes (dell-pc) and the
#   SoC power slider, which the legacy platform_profile can't reach

Name:           dell-xps-ptl-config
Version:        1.3
Release:        2%{?dist}
Summary:        Fedora configuration for Dell XPS on Intel Panther Lake
License:        MIT
URL:            https://github.com/onuralpszr/xps-fedora
BuildArch:      noarch

Source0:        thermald-ptl-adaptive.conf
Source1:        10-sign-dellptl.install
Source2:        xe-psr.conf
Source3:        platform-profile
Source4:        ppd-mapping
Source5:        tuned-xps-ptl-powersave.conf
Source6:        tuned-xps-ptl-balanced.conf
Source7:        tuned-xps-ptl-balanced-battery.conf
Source8:        tuned-xps-ptl-performance.conf

BuildRequires:  systemd-rpm-macros
Requires:       thermald
# Signing hook tools; the key itself comes from `kmodgenca` (akmods)
Requires:       sbsigntools
Requires:       openssl
# initramfs carries xe and modprobe.d options
Requires(posttrans): dracut
Requires:       tuned
Requires:       tuned-ppd
Requires:       python3

%description
thermald drop-in that waits for RAPL, coretemp and the INT3400 DPTF sensors
before starting (Panther Lake is adaptive-only and otherwise ends up with no
thermald), and a kernel-install plugin that re-signs locally built
*.dellptl* kernels with the akmods MOK key for Secure Boot. Also runs the
xe display driver without PSR2 selective fetch (PSR1), which is stable on the
XPS LG OLED panel. Power profiles drive Dell's thermal modes and the SoC
power slider through xps-ptl-* tuned profiles.

%prep

%build

%install
install -Dm644 %{SOURCE0} %{buildroot}%{_unitdir}/thermald.service.d/ptl-adaptive.conf
install -Dm755 %{SOURCE1} %{buildroot}%{_prefix}/lib/kernel/install.d/10-sign-dellptl.install
install -Dm644 %{SOURCE2} %{buildroot}%{_modprobedir}/dell-xps-ptl-xe.conf
install -Dm755 %{SOURCE3} %{buildroot}%{_libexecdir}/dell-xps-ptl/platform-profile
install -Dm755 %{SOURCE4} %{buildroot}%{_libexecdir}/dell-xps-ptl/ppd-mapping
# profile, Dell thermal mode, SoC power slider
while read -r name dell soc; do
    d=%{buildroot}%{_prefix}/lib/tuned/profiles/xps-ptl-$name
    install -Dm644 %{_sourcedir}/tuned-xps-ptl-$name.conf $d/tuned.conf
    printf '#!/bin/bash\nexec %{_libexecdir}/dell-xps-ptl/platform-profile "$1" %s %s\n' \
        "$dell" "$soc" > $d/platform.sh
    chmod 0755 $d/platform.sh
done <<EOF
powersave quiet low-power
balanced balanced balanced
balanced-battery balanced balanced
performance performance performance
EOF

%post
systemctl daemon-reload || :
%{_libexecdir}/dell-xps-ptl/ppd-mapping xps || :
systemctl try-restart tuned.service tuned-ppd.service || :

%preun
if [ $1 -eq 0 ]; then
    %{_libexecdir}/dell-xps-ptl/ppd-mapping default || :
fi

%posttrans
# xe is in the initramfs, so its options must be too
dracut --regenerate-all --force >/dev/null 2>&1 || :

%postun
systemctl daemon-reload || :
if [ $1 -eq 0 ]; then
    systemctl try-restart tuned.service tuned-ppd.service || :
fi

%files
%{_unitdir}/thermald.service.d/ptl-adaptive.conf
%{_prefix}/lib/kernel/install.d/10-sign-dellptl.install
%{_modprobedir}/dell-xps-ptl-xe.conf
%{_libexecdir}/dell-xps-ptl/
%{_prefix}/lib/tuned/profiles/xps-ptl-*/

%changelog
* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.3-2
- Ship the tuned profiles as flat source files and generate their
  platform scripts, so the package builds in COPR

* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.3-1
- tuned-ppd: sysfs_acpi_monitor=false; its hotkey detection read the legacy
  platform_profile as "balanced" and undid every power-saver switch
- platform-profile: no reset on stop

* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.2-1
- xps-ptl-* tuned profiles: power saver = Dell Quiet + SoC low-power,
  balanced = Optimized + balanced, performance = UltraPerformance + performance;
  tuned-ppd mapped to them (restored on removal)

* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.1-1
- xe: enable_psr2_sel_fetch=0 (PSR1) for the LG OLED; rebuild initramfs

* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0-1
- thermald boot-race drop-in and dellptl kernel signing hook
