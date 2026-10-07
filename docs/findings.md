# Findings

What was broken on stock Fedora 45, how it was found, and why each fix looks
the way it does. In the order it was worked through.

## Display: Panel Replay and VRR

- Stock `7.2.9-300.fc45` carries none of Omarchy's `linux-ptl` patches.
  Checked by searching for each patch's unique log string in `xe.ko` and in the
  decompressed `vmlinuz`.
- `dmesg`: `Applying disable Panel Replay quirk`. Upstream turns Panel Replay
  off entirely for the LGD OLED on XPS 14 (`1028:0db9`) and XPS 16
  (`1028:0dba`), because AUX-less ALPM wake/sleep makes the cursor lag. The
  panel then falls back to PSR2 with selective fetch.
  - **0028** replaces that quirk with a workaround: leave Panel Replay on
    frontbuffer activity, re-enter after 50 ms idle.
  - **0020** programs PR_ALPM_CTL only when Panel Replay is actually active.
- `vrr_range` was `0/0`. The EDID has no legacy range descriptor and only a
  DisplayID 2.x Adaptive Sync block (`tag 0x2b`: 20-120 Hz), which stock DRM
  ignores. **0029** fills `monitor_range` from it. KDE then reports VRR as
  capable; the policy defaults to "Never", so set it to "Automatic".
- Chrome YouTube stutter: `chrome://gpu` already showed hardware video decode.
  The stutter went away with the patched kernel.

Kernel: Fedora dist-git f45 at `kernel-7.2.9-300`, patches added as
`Patch1001-1003` + `ApplyOptionalPatch`, `buildid .dellptl`. All three apply
cleanly on top of `patch-7.2-redhat.patch`.

## Secure Boot

- Local Fedora kernel builds come signed with the untrusted
  "Red Hat Test Certifying CA" (`signkernel 0` locally).
- `sbsign` *adds* a second signature after it. Some shim versions only check
  the first one, so `10-sign-dellptl.install` strips every signature
  (`sbattach --remove`) and then signs with the akmods key. It runs as a
  kernel-install plugin before `20-grub.install` copies the image to `/boot`.
- Kernel modules are signed during the kernel build with an ephemeral key
  built into that kernel, so only `vmlinuz` needs the MOK key. akmods signs
  the out-of-tree kmods with the same akmods key.

## Camera (IPU7)

Hardware: IPU7.5 (`8086:b05d`) + OV08X40 behind the Intel CVS vision chip
(`INTC10E1`, USB `06cb:0701`). Stock Fedora loads the staging
`intel_ipu7`/`intel_ipu7_isys` and `intel_cvs`, which give raw Bayer ISYS
nodes only. No PSYS (the image processor) and no HAL.

- **RPM Fusion IPU6 stack**: the HAL detects the platform and asks for
  `libcamhal/plugins/ipu75xa.so`, which only exists in Intel's IPU7 HAL.
  Not usable.
- Ported Omarchy's `intel-ipu7-camera` to two specs (akmod + userspace),
  same pinned commits and patches. Problems on the way:
  1. **Intel's IPU7 firmware**: the same files Fedora ships
     `intel-vsc-firmware` (`ipu7ptl_fw.bin`), so it is not shipped again.
  2. **`intel-vision-drivers` not needed**: 7.2 has `intel_cvs` in-tree.
  3. **ACPI build fails on Fedora**: `serdes-pdata.h` includes
     `media/i2c/lt6911uxe.h` because Fedora enables the mainline
     `CONFIG_VIDEO_LT6911UXE=m`, and mainline has no such header. Omarchy's
     kernel doesn't enable it.
  4. The first build therefore went without ACPI. Result: black camera,
     `intel_ipu7_isys: no subdevice info provided`. In ipu7-drivers, the
     async notifier that binds sensors via `ipu_bridge` / CVS
     (`bind Intel CVS nlanes is 2 port is 0`) is only compiled with
     `CONFIG_INTEL_IPU_ACPI`, so `BUILD_INTEL_IPU_ACPI=1` is required.
  5. Re-enabling ACPI also hits a bit-rotted LT6911 path (`set_csi2()` called
     with 3 of 4 arguments). Patch **0101** force-includes a header that
     `#undef`s the LT6911 Kconfig symbols for this module build only.
  6. **Out-of-tree modules didn't win**: depmod kept picking
     `kernel/drivers/staging/media/ipu7/` over `extra/intel-ipu7/`. The
     out-of-tree PSYS then hangs off the in-tree bus
     (`intel_ipu7.psys.40: deferred probe pending`, no `/dev/ipu7-psys0`).
     Per-module `override` lines in `depmod.d` were ignored (even `depmod -n`);
     `search updates extra built-in weak-updates` works.
  7. HAL build: Fedora's jsoncpp is `/usr/include/json`, but the HAL includes
     `jsoncpp/json/json.h`. Fixed with a symlink in the build staging dir.
  8. rpmbuild: `gstreamer1.prov` loads the plugin to list its elements. The HAL
     logs to stdout while probing, so those log lines became bogus `Provides`.
     The generator is disabled for this package.
  9. Fedora's `v4l2-relayd`: a generator starts `v4l2-relayd@<name>` for every
     `/etc/v4l2-relayd.d/*.conf`, so `ipu7.conf` is enough. Its unit has
     `LimitNPROC=1` with an empty capability set, which would stop the
     multithreaded HAL. The drop-in relaxes that, orders after
     `camera-init.service` and opens up the device sandbox. The loopback card
     keeps Fedora's label "Intel MIPI Camera" (`/dev/video50`).
- **Initramfs regression (2026-10-07):** after `dell-xps-ptl-config` 1.1 ran
  `dracut --regenerate-all`, host-only dracut put the loaded IPU7 akmod
  modules into the initramfs without `intel/ipu/ipu7ptl_fw.bin`. The bus
  driver probed at ~2 s (root mounts at ~15 s), failed with `-ENOENT` and
  never retried: no `/dev/ipu7-psys0`, no camera. Fix in
  `intel-ipu7-camera` 1.0.6-3: `omit_drivers` for the IPU7 modules in
  `/usr/lib/dracut/dracut.conf.d/90-intel-ipu7-camera.conf` + regenerate.
  Live recovery: `echo 0000:00:05.0 > /sys/bus/pci/drivers/intel-ipu7/bind`,
  then restart `v4l2-relayd@ipu7`. Lesson: anything that regenerates
  initramfs can pull firmware-dependent drivers into early boot.
- akmod rather than DKMS: same layout as RPM Fusion's `intel-ipu6-kmod`, and
  akmods signs with the already enrolled key.

## Thermal

- `thermald` was inactive. Fedora's unit already passes `--adaptive`, and
  Panther Lake (`6:204`) is adaptive-only in thermald 2.5.13.
- The first start at boot logs `NO RAPL sysfs present`,
  `No coretemp sysfs found`, then `Adaptive policy couldn't create any zones /
  Possibly some sensors in the PSVT are missing`. thermald writes
  `/run/thermald/ignore_adaptive`, exits, and systemd restarts it in
  non-adaptive mode, which refuses the CPU (`Unsupported cpu model`). The
  result is no thermald for the whole boot.
- Dell's data vault (`INTC10D4:00/data_vault`, `gddv`, "OEM Exported
  DataVault") is fine. Started after the sensors exist (`SEN1` to `SEN7`,
  `TCPU`, `TCPU_PCI`, RAPL, coretemp), thermald keeps running and takes every
  zone into `user_space`.
- Fix (`dell-xps-ptl-config`): drop-in that clears the marker and waits up to
  30 s for RAPL, coretemp and `TCPU` before starting.
- `intel-lpmd` and `tuned` + `tuned-ppd` run fine as they are.

## NPU

- Fedora `intel-npu-driver` is built with `ENABLE_NPU_COMPILER_BUILD=OFF` and
  ships only `libze_intel_npu.so`. OpenVINO 2026.4 fails with
  `Unsupported configuration key: NPU_MAX_TILES`.
- Intel's v1.38 release (verified with OpenVINO 2026.3.1) ships the compiler
  prebuilt: `libopenvino_intel_npu_compiler.so` + `_loader.so`.
- The driver and compiler versions have to match. 1.32 dlopens
  `libnpu_driver_compiler.so`, while 1.38 loads
  `libopenvino_intel_npu_compiler_loader.so`. So the package is Fedora's spec
  updated to 1.38 (built from source) plus an `intel-npu-compiler` subpackage
  with Intel's prebuilt compiler.
- Firmware: Fedora's `intel-npu-firmware` works; Intel's newer
  `vpu_50xx_v1.bin` is not needed.

## Display: DSB poll errors, FIFO underruns and a stuck PSR (open)

- Seen on `300.1` (and DSB poll errors already on `300`: 187 in one boot).
  Opening Spectacle's screenshot overlay was followed within 0.6 s by
  `[CRTC:151:pipe A] DSB 0 poll error` (×22), then `CPU pipe A FIFO underrun`,
  then `Timed out waiting for PSR Idle for re-enable` ~8/s (500+), with heavy
  artifacts on every mouse move. VRR on/off makes no difference.
- The timeout message comes from `__psr_wait_for_idle_locked()`, which patch
  0028's delayed Panel Replay re-enable calls on every frontbuffer flush.
- Recovery without reboot: `kscreen-doctor --dpms off; sleep 3;
  kscreen-doctor --dpms on` (re-initializes PSR). Writing
  `i915_edp_psr_debug` doesn't work: Secure Boot lockdown blocks debugfs writes.
- Isolating: `xe.enable_dsb=0` (keep Panel Replay) vs
  `xe.enable_panel_replay=0` (PSR2 like stock), one boot each, repro =
  Spectacle overlay + mouse movement.

### Test: ALPM fast-wake quirk instead of 0028 (`300.2`)

- Upstream root-cause candidate: [PATCH v2] "drm/i915/alpm: Add a quirk to keep
  the fast wake ahead of the IO buffer wake" (Jake Steinman, intel-gfx,
  Message-ID 20260903131724.49496-1-j@metarealtyinc.ca, not merged). On the LG
  00:22:b9 panel the spec formulas give fast wake == IO buffer wake (11/11
  lines at 3200x2000@120), and every ALPM link wake then fails with a Link CRC
  error (70/71 polls); fast > IO gives 0/71. v1 was generic; Intel (Jouni
  Högander) asked for a panel quirk, hence v2.
- The author says it does not by itself make Panel Replay or PSR2 selective
  updates work: with clean wakes the panel "never receives a selective
  update" (separate thread). If the screen updates late/wrong on `300.2`, add
  `xe.enable_psr2_sel_fetch=0`.
- `300.2` = 0020 + 0029 + ALPM v2 (0034), without 0028 (Panel Replay stays off
  via the upstream quirk, display on PSR2) and without the ipu-bridge HM1092
  entry (0030), which blocked the RGB camera while the HM1092 can't probe.
  Patch obtained as the raw lore message, applies to 7.2.9 + 0020 without fuzz.

Result on `300.2` (2026-10-06):
- ALPM quirk + upstream "disable Panel Replay" quirk active: 0 PSR idle
  timeouts / DSB poll errors / underruns (hundreds before), RGB camera back.
- But PSR2 selective updates then misbehave exactly as the author predicted:
  UI glitches, screen feels frozen.
- `xe.enable_psr2_sel_fetch=0`: smooth, 0 errors. On display 20+ PSR2 needs
  selective fetch, so this ends up as **PSR1** (`PSR mode: PSR1 enabled`,
  status `SRDENT`): panel self-refresh on static screens, full frames on
  updates. PSR1 doesn't use ALPM, so the quirk is inert there (kept, harmless).
- **Current setup: `300.2` + `xe.enable_psr2_sel_fetch=0`.** Revisit when the
  selective-update bug (separate intel-gfx thread, drm/xe #7521) is fixed.

## IR camera (Himax HM1092)

- The Windows Hello IR sensor is a Himax HM1092 (ACPI `HIMX1092`, `\_SB_.LNK0`,
  enabled). The three `OVTI01AF` entries are disabled BIOS placeholders.
  Power, reset and the IR flood LED come from `INT3472:00` (int3472-discrete),
  which already exposes `/sys/class/leds/HIMX1092_00::ir_flood_led`.
- No driver on stock 7.2. Upstream state (2026-10):
  - `media: ipu-bridge: Add Himax HM1092 IR sensor` (v2): accepted in
    media.git, expected in 7.3.
  - `media: i2c: hm1092` driver: v6 on linux-media, still in review. Tested
    on an ASUS Zenbook A14 (Snapdragon, devicetree) only.
- v6 cannot bind on x86 as posted: it has only an OF match table, and it fails
  permanently ("parsing endpoint failed") if it probes before ipu-bridge
  creates the fwnode endpoint. Patch 0033 adds the `HIMX1092` ACPI ID and
  `-EPROBE_DEFER` while the endpoint is missing, like `ov08x40`.
- IR flood LED: upstream deliberately gives it no kernel consumer (the v4l2
  core only drives the *privacy* LED). Userspace switches the LED class device
  around a capture.
- First boot on `300.1`: ACPI match and ipu-bridge work ("Found supported
  sensor HIMX1092:00"), but probe fails: `external clock 19200000 is not
  supported`. Intel boards clock it at 19.2 MHz; v6 only has the Zenbook's
  24 MHz PLL setup (/12 ×90 = 180 MHz). 19.2 MHz /8 ×75 gives the same link.
- With the ipu-bridge entry present but hm1092 failing to probe, the ISYS
  async notifier never completes ("All sensor registration completed" never
  appears), so the RGB camera breaks too (`VIDIOC_STREAMON: Broken pipe`).
  The ipu-bridge entry (0030) must only ship together with a working hm1092.
- Kernel: patches 0030-0033 as `Patch1004-1007`, `CONFIG_VIDEO_HM1092=m` in
  `kernel-local`, release `300.1` so it installs next to `300`.

### Upstream state (checked 2026-10-06)

- `ipu-bridge: Add Himax HM1092 IR sensor` (Jake Steinman, v2): **accepted**,
  in media.git/next (for 7.3). Its two link frequencies are 180.48 MHz for Dell
  (19.2 MHz EXTCLK) and 180 MHz for ASUS (24 MHz).
- Two competing sensor drivers, neither reviewed by the maintainers yet:
  - Ramshouriesh R v6 (2026-08-01): DT-only, 24 MHz only, tested on ASUS
    Zenbook A14 (Snapdragon). Rejects our 19.2 MHz clock.
  - Jake Steinman (2026-07-26): ACPI `HIMX1092`, x86 IPU6/IPU7, **tested on
    Dell XPS 16 DA16260 / Panther Lake**, 648x368, link 180.48 MHz, optional
    clock. Init table (238 regs) extracted from the Windows `hm1092.sys` and
    checked against a bus capture, which may be a provenance concern upstream.
    A reply pointed at the earlier series; Ramshouriesh wants "one good driver".
- The IR sensor sits **behind the Intel CVS / Synaptics SVP7500 bridge** too.
  The 7.2 `drivers/media/i2c/cvs` driver handles one sink (port 0, RGB) and
  rejects sink/source lane mismatch (HM1092 = 1 lane in, 2 out). Intel (Miguel
  Vadillo, platform-driver-x86, 2026-05-15) agreed that check is wrong and
  posted a fix; a "secure handshake" gate on IR port 2 was left open ("not
  currently expecting to handle the IR winhello camera").
- omarchy#8641 (XPS 14): sensor never answers on I2C; CVS likely gates its
  power/ownership.
- So a working IR camera on this machine needs: a sensor driver that accepts
  19.2 MHz (Jake's), CVS changes for the IR port (lanes, routing, maybe the
  handshake), then the ipu-bridge entry. Only Jake has reported frames on a
  DA16260.

### Face login decision (2026-10-06)

- Not Howdy: last stable release 2020, 3.0 beta unreleased for years, forks
  early WIP. Plan: **Gaze** (GunduLabs, Rust, SCRFD + ArcFace + liveness,
  PAM to `gazed` over D-Bus, TPM-sealed templates, Fedora 45 COPR, `gaze-kde`,
  OpenVINO/NPU).
- IR face login is blocked in hardware support, not by the face-login tool:
  no IR frames reach Linux until the CVS bridge passes the IR stream (see
  above). Gaze would need an 8-bit GREY V4L2 node (relay from IPU7 raw10) and
  a sysfs-LED emitter profile for `HIMX1092_00::ir_flood_led`.
- RGB-only face login works with the current webcam but can be fooled by
  photos more easily (liveness model helps). If used at all: lock screen
  only, never sudo/SDDM/LUKS, password always as fallback.
- Next: ask Jake Steinman how he got IR frames through the CVS bridge on the
  DA16260; watch linux-media for a merged HM1092 driver + CVS multi-sensor.

## Power profiles: Dell thermal modes + SoC slider

- Two platform-profile handlers: `dell-pc` (cool/quiet/balanced/performance =
  BIOS `ThermalManagement` Cool/Quiet/Optimized/UltraPerformance, switched at
  runtime) and Intel's "SoC Power Slider" (low-power/balanced/performance).
  The legacy `/sys/firmware/acpi/platform_profile` only offers what both
  share (balanced/performance), so tuned's power-saver request
  (`low-power|quiet`) reached neither.
- `dell-xps-ptl-config` ≥ 1.2: `xps-ptl-{powersave,balanced,balanced-battery,
  performance}` tuned profiles include Fedora's and add a script instance
  that sets each handler by name; tuned-ppd's `/etc/tuned/ppd.conf` is mapped
  to them (original kept as `ppd.conf.dell-xps-ptl.orig`, restored on removal).
- 1.3: tuned-ppd's `sysfs_acpi_monitor` treats legacy platform_profile changes
  it didn't make as a firmware hotkey and switches to match. With the two
  handlers moving, it read "balanced" and undid every power-saver switch
  (tuned log: profile applied, then `stop full_rollback` 1 ms later). Monitor
  disabled; the XPS has no such hotkey. Script `stop` is a no-op.
- Verified: power saver = quiet / low-power / EPP power / no turbo (legacy
  `custom`); balanced = balanced / balanced; performance = performance /
  performance / EPP performance.
- tuned-ppd has no `powerprofilesctl`; use KDE's slider or
  `sudo tuned-adm profile xps-ptl-…`. Don't install power-profiles-daemon (it
  conflicts with tuned-ppd).

## Auto-brightness

- Sensors: ISH ALS via iio-sensor-proxy (`HasAmbientLight`, lux); readings
  only update while a client holds `ClaimLight`. PowerDevil 6.7.5 has no
  ambient-light support, so `xps-ptl-tools` adds a user service.
- Control path: KDE `org.kde.ScreenBrightness/display0` (0-10000),
  `SetBrightness(value, flags)`; flag 0x1 suppresses the OSD. KDE sends
  `BrightnessChanged` on the root object plus `PropertiesChanged` on the
  display, and re-announces unchanged values (must not count as user changes).
- Pitfalls hit while building it:
  - iio-sensor-proxy only signals changes: poll `LightLevel` every tick, or a
    smoothed value gets stuck when the room is steady.
  - Don't adopt the session's start brightness as the preference; persist the
    learned offset instead (`~/.local/state/xps-ptl/autobrightness`).
  - The ALS reports **bursts of impossible values**: median 1 lx in a dark
    room, but 15 338 and 114 697 lx for 0.5-1.5 s at a time (both ALS
    devices; not the screen's own light, which moves it only 0 to 1 lx from
    10 % to 90 %). Fix: 0.5 s sampling, drop > 40 000 lx, 30th percentile of
    a 6 s window, then smoothing.
  - Wayland KDE has no `GetSessionIdleTime` and no logind IdleHint, so idle
    dimming is detected as a sharp drop (≤ 50 %) and waits for the restore.
- Widget (`org.xpsptl.autobrightness`): `org.kde.plasma.workspace.dbus`
  (`Properties` for live values, `SessionBus.asyncCall` for methods). Its
  `DBusServiceWatcher.registered` only changes on events, so check
  `NameHasOwner` too. Popups need `Layout.minimumHeight`/`preferredHeight`
  in the panel or they collapse to the header.
- Packaging: no systemd preset (a preset enables the unit globally for every
  user); users run `systemctl --user enable --now xps-ptl-autobrightness`.
- Icons are original (screen + sensor + light rays), not Dell trademarks.

## Copilot key

- Sends `LEFTMETA + LEFTSHIFT + F23`. xkeyboard-config 2.48 maps
  Shift+Super+`<FK23>` to `XF86Assistant` (`PC_SHIFT_SUPER_LEVEL2`), and Qt 6.11
  has no key for it, so KDE can't bind it.
- `fkeys:basic_13-24` would fix it but also turns F20 (MicMute) and F21/F22
  (touchpad) into plain F-keys. Instead input-remapper maps F23 to F19 and KDE
  binds Meta+Shift+F19 (`tools/copilot-key`).
- Upstream: Qt has no `Key_Assistant` for `XF86Assistant`.

## External displays

- Direct HDMI from the laptop: 4K60 fine.
- Anker USB-C hub (`291a:8383`, VIA Labs USB hubs, AX88179 Ethernet,
  NS1081 card reader): DisplayPort Alt Mode (`svid ff01`), not DisplayLink.
  USB, Ethernet and card reader work. The monitor (4K60 / 1440p144 capable)
  went black or cycled at high refresh rates and settled at 60 Hz: the hub
  runs USB 3 alongside DP, so DP gets 2 lanes (~8.6-13 Gbit/s), too little
  for 4K60 / 1440p120+. Dock limit, not Linux; use 60 Hz, 4K30, or a
  4-lane / Thunderbolt dock.
- Keyboard backlight: all levels work.

## Not hardware problems

- **Fingerprint**: the DA16260 has none (Dell spec page; nothing on
  USB/I2C/SPI). `06cb:0701` is the CVS camera bridge, not a reader. The
  machine has an IR camera (`HIMX1092` flood LED, `OVTI01AF`) for face login
  instead.
- **Touchpad haptics**: the touchpad is `2C2F:0033`. Omarchy's
  `dell-xps-touchpad-haptics` targets a Synaptics part, so it doesn't apply.
- **Codecs**: Fedora's `libva-intel-media-driver` has no H.264/HEVC; RPM
  Fusion's `intel-media-driver` has them.

## Human presence sensor

Intel "Human Presence v2" (HID 0x200011, model `HuP v2`, detection type
*facial*) behind the ISH (`ish_ptl_39ceeaf8.bin`, FW 5.8.1.7783). It is
camera based: the Synaptics SVP7xxx CVS (06CB:0701) runs the vision model on
frames from the RGB sensor (ov08x40). Linux exposes it as iio `prox`
(`hid-sensor-prox`); the sensor's own state field is only visible in the raw
HID reports (`plasma-sensord/tools/hpd-diag.py`).

Result: **not usable on Linux** (BIOS 1.8.2, kernel 7.2.9).

| Condition | Sensor |
|---|---|
| sysfs `_raw` reads | presence -1 / 65535 (no data) |
| buffered stream, camera idle | `NOT AVAILABLE`, then silent |
| ov08x40 runtime-PM forced on, not streaming | `READY`, then silent |
| test `intel_cvs` with `ICVS_HOST_VISION_SENSING` | no change |
| BIOS `HPDSensor=IntelHPD` (default `MSHPD`) | identical |
| camera streaming to an app | ~4 s presence bursts on motion only |

The CVS only sees frames while the host streams; the standalone CVS mode
(the chip driving the sensor itself) is not set up by anything on Linux.
Four ISH clients have no Linux driver: 1F050626-…, A7216DFB-…, BB579A2E-…,
C1CC78B9-…. Needs Intel/Synaptics; report together with the CVS/IR thread.

## Still open

- `xe` `[PLANE:135:plane 5A] fault`: also on the stock kernel. Shows up when a
  camera/video window opens in KWin (likely an overlay-plane buffer freed
  while still being scanned out). No visible effect so far.
- Camera suspend/resume works (brief green flash on open: relay starts before the first ISP frame; a black SPLASHSRC would hide it).
- IR camera + Howdy.
- thermald fix: confirm over several cold boots.
