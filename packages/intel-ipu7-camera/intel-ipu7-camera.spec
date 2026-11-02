# Intel IPU7 MIPI camera stack for Dell XPS 14/16 (Panther Lake, OV08X40 behind
# Intel CVS). Fedora port of omarchy-pkgs pkgbuilds/intel-ipu7-camera.

%global bins_commit    0525cdfb501b56dcffbacd4e46a13c63ab0f2866
%global hal_commit     30ad691a040142e362e5ea0158460366386b9465
%global icsrc_commit   4fb31db76b618aae72184c59314b839dedb42689

# Prebuilt Intel imaging libraries: don't strip or generate debuginfo
%global debug_package %{nil}
%global __strip /bin/true
# gstreamer1.prov runs the plugin, and the HAL logs to stdout during probing
%global __gstreamer1_provides %{nil}

Name:           intel-ipu7-camera
Version:        1.0.6
Release:        8.dellptl%{?dist}
Summary:        Intel IPU7 MIPI camera stack (OV08X40 + hardware ISP)
License:        GPL-2.0-or-later AND Apache-2.0 AND LGPL-2.1-or-later AND LicenseRef-Intel-Proprietary
URL:            https://github.com/intel/ipu7-camera-hal
ExclusiveArch:  x86_64

Source1:        https://github.com/intel/ipu7-camera-bins/archive/%{bins_commit}/ipu7-camera-bins-%{bins_commit}.tar.gz
Source2:        https://github.com/intel/ipu7-camera-hal/archive/%{hal_commit}/ipu7-camera-hal-%{hal_commit}.tar.gz
Source3:        https://github.com/intel/icamerasrc/archive/%{icsrc_commit}/icamerasrc-%{icsrc_commit}.tar.gz

Source12:       camera-deps.conf
Source13:       v4l2loopback-ipu7.conf
Source14:       camera-init.service
Source15:       v4l2-relayd-ipu7.conf
Source16:       v4l2-relayd-ipu7-override.conf
Source17:       hide-ipu7-v4l2.conf
Source18:       disable-libcamera.conf
Source19:       70-ipu7-psys.rules
Source20:       71-ipu7-hide-isys.rules
Source21:       camera-tmpfiles.conf
Source22:       camera-sleep-hook

# ipu7-camera-hal
Patch11:        0006-camhal-ipu75xa-ov08x40-Intel-CVS-formats.patch
Patch12:        0012-camhal-ipu7x-ov08x40-Intel-CVS-formats.patch
Patch13:        0008-camhal-honor-the-reduced-YUV-color-range.patch
Patch14:        0010-camhal-scale-analog-gain-codes-to-the-ov08x40-driver-units.patch
Patch15:        0011-camhal-fall-back-to-the-default-ISP-tuning-when-the-mode-is-missing.patch
Patch16:        0013-camhal-load-the-module-NVM-from-a-file-named-in-the-sensor-config.patch
# icamerasrc
Patch20:        0009-icamerasrc-add-an-fps-range-property-for-auto-exposure.patch

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  make
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libdrm_intel)
BuildRequires:  pkgconfig(jsoncpp)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(gstreamer-1.0)
BuildRequires:  pkgconfig(gstreamer-plugins-base-1.0)
BuildRequires:  pkgconfig(gstreamer-video-1.0)
BuildRequires:  pkgconfig(gstreamer-allocators-1.0)
BuildRequires:  pkgconfig(gstreamer-va-1.0)
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(libva-drm)
BuildRequires:  systemd-rpm-macros

# Kernel modules come from the akmod (intel-ipu7-kmod.spec)
# depmod and dracut settings for the akmod are in intel-ipu7-kmod-common
Requires:       intel-ipu7-kmod >= %{version}
Requires:       intel-ipu7-kmod-common >= 1.0.6-6
Requires:       v4l2-relayd
Requires:       v4l2loopback
Requires:       gstreamer1-plugins-base
Requires:       gstreamer1-plugins-good
Requires:       gstreamer1-plugins-bad-free
Conflicts:      ipu6-camera-hal
Conflicts:      gstreamer1-plugins-icamerasrc

# Prebuilt libs link against each other; don't auto-require them by soname
%global __requires_exclude ^lib(ia_|gcss|ipu|iacss|broxton|camhal).*$
%global __provides_exclude_from ^%{_libdir}/libcamhal/plugins/.*$

%description
Intel IPU7 camera HAL (ipu7x/ipu75xa plugins), Intel imaging libraries,
the icamerasrc GStreamer element and the v4l2-relayd/v4l2loopback glue that
exposes the Dell XPS 14/16 OV08X40 camera as a regular webcam.

%prep
%setup -q -c -T -a 1 -a 2 -a 3
mv ipu7-camera-bins-%{bins_commit} ipu7-camera-bins
mv ipu7-camera-hal-%{hal_commit} ipu7-camera-hal
mv icamerasrc-%{icsrc_commit} icamerasrc
# Each component keeps its own license text
cp -p ipu7-camera-bins/LICENSE LICENSE.ipu7-camera-bins
cp -p ipu7-camera-hal/LICENSE LICENSE.ipu7-camera-hal
cp -p icamerasrc/LICENSE LICENSE.icamerasrc

pushd ipu7-camera-hal
%patch -P11 -p1
%patch -P12 -p1
%patch -P13 -p1
%patch -P14 -p1
%patch -P15 -p1
%patch -P16 -p1
popd
pushd icamerasrc
%patch -P20 -p1
popd

# Stage prebuilt libs/headers for build-time use
staging=$PWD/staging
mkdir -p $staging/usr/lib $staging/usr/include $staging/usr/lib/pkgconfig
cp -P ipu7-camera-bins/lib/lib* $staging/usr/lib/
cp -r ipu7-camera-bins/include/* $staging/usr/include/
cp -r ipu7-camera-bins/lib/pkgconfig/* $staging/usr/lib/pkgconfig/
sed -i "s|^prefix=.*|prefix=$staging/usr|" $staging/usr/lib/pkgconfig/*.pc

# The HAL includes <jsoncpp/json/json.h>; Fedora ships /usr/include/json
mkdir -p $staging/usr/include/jsoncpp
ln -sf %{_includedir}/json $staging/usr/include/jsoncpp/json

%build
staging=$PWD/staging
export PKG_CONFIG_PATH=$staging/usr/lib/pkgconfig:%{_libdir}/pkgconfig:%{_datadir}/pkgconfig
export LIBRARY_PATH=$staging/usr/lib
export LD_LIBRARY_PATH=$staging/usr/lib
export CPATH=$staging/usr/include

pushd ipu7-camera-hal
cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_INSTALL_SYSCONFDIR=%{_sysconfdir} \
    -DBUILD_CAMHAL_ADAPTOR=ON \
    -DBUILD_CAMHAL_PLUGIN=ON \
    -DIPU_VERSIONS="ipu7x;ipu75xa" \
    -DUSE_STATIC_GRAPH=ON \
    -DUSE_STATIC_GRAPH_AUTOGEN=ON \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DCMAKE_PREFIX_PATH=$staging/usr \
    -DCMAKE_LIBRARY_PATH=$staging/usr/lib \
    -DCMAKE_INCLUDE_PATH=$staging/usr/include
%make_build -C build
make -C build DESTDIR=$staging/hal install
popd

# icamerasrc builds against the freshly built HAL
halroot=$staging/hal%{_prefix}
install -Dm644 ipu7-camera-hal/libcamhal.pc $staging/usr/lib/pkgconfig/libcamhal.pc
sed -i "s|^prefix=.*|prefix=$halroot|" $staging/usr/lib/pkgconfig/libcamhal.pc
export LIBRARY_PATH=$halroot/%{_lib}:$LIBRARY_PATH
export LD_LIBRARY_PATH=$halroot/%{_lib}:$LD_LIBRARY_PATH
export CPATH=$halroot/include:$CPATH

pushd icamerasrc
export CHROME_SLIM_CAMHAL=ON
./autogen.sh
%configure --disable-static
%make_build
popd

%install
# --- HAL (plugins + adaptor + /etc/camera configs) ---
make -C ipu7-camera-hal/build DESTDIR=%{buildroot} install
# serdes firmware for the ISX031 automotive sensors (IoT boards), not used here
rm -f %{buildroot}/boot/max96724_isx031_ipu75xa.img

pushd ipu7-camera-hal/config/linux/ipu75xa
install -Dm644 libcamhal_configs.json -t %{buildroot}%{_datadir}/defaults/etc/camera/
install -Dm644 *.aiqb -t %{buildroot}%{_datadir}/defaults/etc/camera/
popd

# --- Prebuilt Intel imaging libraries + headers ---
pushd ipu7-camera-bins
install -d %{buildroot}%{_libdir} %{buildroot}%{_includedir} %{buildroot}%{_libdir}/pkgconfig
cp -P lib/lib* %{buildroot}%{_libdir}/
cp -r include/* %{buildroot}%{_includedir}/
cp lib/pkgconfig/*.pc %{buildroot}%{_libdir}/pkgconfig/
sed -i 's|^libdir=.*|libdir=${exec_prefix}/%{_lib}|' %{buildroot}%{_libdir}/pkgconfig/*.pc
popd

# --- icamerasrc ---
make -C icamerasrc DESTDIR=%{buildroot} install
find %{buildroot} -name '*.la' -delete

# --- System integration ---
install -Dm644 %{SOURCE12} %{buildroot}%{_modprobedir}/ipu7-camera-deps.conf
install -Dm644 %{SOURCE13} %{buildroot}%{_sysconfdir}/modprobe.d/v4l2-relayd.conf
install -Dm644 %{SOURCE14} %{buildroot}%{_unitdir}/camera-init.service
install -Dm644 %{SOURCE15} %{buildroot}%{_sysconfdir}/v4l2-relayd.d/ipu7.conf
install -Dm644 %{SOURCE16} %{buildroot}%{_unitdir}/v4l2-relayd@ipu7.service.d/ipu7.conf
install -Dm644 %{SOURCE17} %{buildroot}%{_datadir}/wireplumber/wireplumber.conf.d/hide-ipu7-v4l2.conf
install -Dm644 %{SOURCE18} %{buildroot}%{_datadir}/wireplumber/wireplumber.conf.d/disable-libcamera.conf
install -Dm644 %{SOURCE19} %{buildroot}%{_udevrulesdir}/70-ipu7-psys.rules
install -Dm644 %{SOURCE20} %{buildroot}%{_udevrulesdir}/71-ipu7-hide-isys.rules
install -Dm644 %{SOURCE21} %{buildroot}%{_tmpfilesdir}/ipu7-camera.conf
install -Dm755 %{SOURCE22} %{buildroot}%{_prefix}/lib/systemd/system-sleep/ipu7-camera

%post
/sbin/ldconfig
systemd-tmpfiles --create %{_tmpfilesdir}/ipu7-camera.conf || :
udevadm control --reload-rules 2>/dev/null || :
systemctl daemon-reload || :
systemctl enable camera-init.service || :

%preun
if [ $1 -eq 0 ]; then
    systemctl disable --now camera-init.service 'v4l2-relayd@ipu7.service' 2>/dev/null || :
fi

%postun
/sbin/ldconfig
systemctl daemon-reload || :

%files
%license LICENSE.ipu7-camera-bins LICENSE.ipu7-camera-hal LICENSE.icamerasrc
%{_libdir}/lib*.so*
%{_libdir}/libcamhal/
%{_libdir}/pkgconfig/ia_imaging-*.pc
%{_libdir}/pkgconfig/libcamhal.pc
%{_libdir}/pkgconfig/libgsticamerasrc.pc
%{_includedir}/libcamhal/
%{_libdir}/gstreamer-1.0/libgsticamerasrc.so*
%{_includedir}/ipu7x/
%{_includedir}/ipu75xa/
%{_includedir}/ipu8/
%{_includedir}/gstreamer-1.0/
%config(noreplace) %{_sysconfdir}/camera/
%{_datadir}/defaults/etc/camera/
%{_modprobedir}/ipu7-camera-deps.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/v4l2-relayd.conf
%config(noreplace) %{_sysconfdir}/v4l2-relayd.d/ipu7.conf
%{_unitdir}/camera-init.service
%{_unitdir}/v4l2-relayd@ipu7.service.d/
%{_datadir}/wireplumber/wireplumber.conf.d/*.conf
%{_udevrulesdir}/70-ipu7-psys.rules
%{_udevrulesdir}/71-ipu7-hide-isys.rules
%{_tmpfilesdir}/ipu7-camera.conf
%{_prefix}/lib/systemd/system-sleep/ipu7-camera

%changelog
* Mon Nov 02 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-8.dellptl
- Update ipu7-camera-hal to 30ad691 and ipu7-camera-bins to 0525cdf
  (Intel IPU7 release of 2026-09-26, new OV08X40_KAFE799 graph)
- Do not ship the ISX031 serdes image the new HAL installs to /boot

* Mon Nov 02 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-7.dellptl
- Move the depmod and dracut settings to intel-ipu7-kmod-common and stop
  providing it here, so the akmod installs from the COPR on its own (#36)

* Mon Oct 19 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-6.dellptl
- Load the OV08X40 module NVM (lens shading and AWB calibration) from
  /var/lib/intel-ipu7-camera/ov08x40-uf.nvm when present

* Mon Oct 19 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-5.dellptl
- Update ipu7-camera-hal to 42d26ec and ipu7-camera-bins to adf5552 (new
  OV08X40 graph, AIQ/AIC/CCA libraries)
- Drop the CVS routing backport, upstream since 4de10b6
- Rebase the analog gain scaling patch on the new SensorHwCtrl

* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-4.dellptl
- Ship the license of each component, including the Intel camera binaries

* Wed Oct 07 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-3.dellptl
- dracut: omit the IPU7 drivers from the initramfs; host-only dracut pulled
  them in without ipu7ptl_fw.bin and the probe failed with -ENOENT at boot

* Tue Oct 06 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-2.dellptl
- depmod.d: use "search ... extra built-in" so the akmod IPU7 bus/ISYS win over staging

* Mon Oct 05 2026 Onuralp SEZER <thunderbirdtr@fedoraproject.org> - 1.0.6-1.dellptl
- Fedora port of omarchy intel-ipu7-camera 1.0.6 for Dell XPS 16 DA16260
