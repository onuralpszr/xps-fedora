# 🔎 Findings

What was broken on stock Fedora 45 on the Dell XPS 16 DA16260, how it was tracked down, and why each fix looks the way it does. The short version is the table below; open the dropdowns for the debugging notes.

✅ fixed, ⚠️ partly fixed or open, ⛔ blocked upstream, ℹ️ not a Linux problem

## Summary

| | Area | Status | Fix |
| --- | --- | :---: | --- |
| 🌈 | [VRR](#display-vrr) | ✅ | kernel patch 0029 reads the DisplayID Adaptive Sync range |
| ✨ | [Panel self refresh](#display-panel-self-refresh) | ✅ | ALPM fast wake quirk (0034) and PSR1 through `xe.enable_psr2_sel_fetch=0` |
| 🔐 | [Secure Boot](#secure-boot) | ✅ | kernel-install hook signs with the akmods key |
| 📷 | [Camera](#camera-ipu7) | ✅ | `intel-ipu7-kmod` with ACPI, `intel-ipu7-camera`, `v4l2-relayd` |
| 🙂 | [IR camera](#ir-camera-himax-hm1092) | ⛔ | the CVS bridge does not pass IR frames yet |
| ⚡ | [NPU](#npu) | ✅ | `intel-npu-driver` 1.38 with Intel's compiler |
| ❄️ | [Thermal](#thermal) | ✅ | thermald waits for the sensors before starting |
| 🎚️ | [Power profiles](#power-profiles) | ✅ | tuned profiles that set both platform profile handlers |
| 💡 | [Ambient light](#ambient-light) | ✅ | plasma-light-and-presence |
| 👤 | [Presence sensor](#presence-sensor) | ⛔ | camera based, needs Intel or Synaptics |
| 🤖 | [Copilot key](#copilot-key) | ✅ | input-remapper maps F23 to F19 |
| 🔌 | [External displays](#external-displays) | ℹ️ | refresh rate depends on the dock or adapter |
| 🎬 | [Codecs, fingerprint, haptics](#not-hardware-problems) | ℹ️ | not hardware problems |

The kernel in use is `7.2.9-300.2.dellptl` with patches 0020, 0029, 0031 to 0033 and 0034, plus `xe.enable_psr2_sel_fetch=0` from `dell-xps-ptl-config`.

## Display: VRR

The panel's `vrr_range` was `0/0`. The EDID has no legacy range descriptor, only a DisplayID 2.x Adaptive Sync block (tag `0x2b`, 20 to 120 Hz), which stock DRM ignores. Patch **0029** fills `monitor_range` from it. KDE then reports VRR as capable, but its policy defaults to "Never", so set it to "Automatic".

<details>
<summary>How it was found</summary>

- Stock `7.2.9-300.fc45` carries none of Omarchy's `linux-ptl` patches. Checked by searching for each patch's unique log string in `xe.ko` and in the decompressed `vmlinuz`.
- Chrome YouTube stutter: `chrome://gpu` already showed hardware video decode. The stutter went away with the patched kernel.
- Kernel packaging: Fedora dist-git f45 at `kernel-7.2.9-300`, patches added as `Patch1001` onwards with `ApplyOptionalPatch`, `buildid .dellptl`. They apply cleanly on top of `patch-7.2-redhat.patch`.

</details>

## Display: panel self refresh

The current setup is **PSR1**: the panel refreshes itself on a static screen and gets full frames on updates. It runs with 0 errors and no glitches. Revisit PSR2 when the selective update bug (drm/xe #7521) is fixed.

<details>
<summary>Panel Replay and the first patch set (0020, 0028)</summary>

- `dmesg`: `Applying disable Panel Replay quirk`. Upstream turns Panel Replay off for the LGD OLED on XPS 14 (`1028:0db9`) and XPS 16 (`1028:0dba`), because AUX-less ALPM wake and sleep make the cursor lag. The panel then falls back to PSR2 with selective fetch.
- **0028** replaced that quirk with a workaround: leave Panel Replay on frontbuffer activity, re-enter after 50 ms idle. It is no longer applied.
- **0020** programs `PR_ALPM_CTL` only when Panel Replay is actually active. Still applied.

</details>

<details>
<summary>DSB poll errors, FIFO underruns and a stuck PSR on 300 and 300.1</summary>

- DSB poll errors already on `300` (187 in one boot). Opening Spectacle's screenshot overlay was followed within 0.6 s by `[CRTC:151:pipe A] DSB 0 poll error` (22 times), then `CPU pipe A FIFO underrun`, then `Timed out waiting for PSR Idle for re-enable` about 8 times a second (500+), with heavy artifacts on every mouse move. VRR on or off made no difference.
- The timeout message comes from `__psr_wait_for_idle_locked()`, which 0028's delayed Panel Replay re-enable calls on every frontbuffer flush.
- Recovery without a reboot: `kscreen-doctor --dpms off; sleep 3; kscreen-doctor --dpms on` re-initializes PSR. Writing `i915_edp_psr_debug` does not work, because Secure Boot lockdown blocks debugfs writes.

</details>

<details>
<summary>The ALPM fast wake quirk and the move to PSR1 (300.2)</summary>

- Root cause candidate: "drm/i915/alpm: Add a quirk to keep the fast wake ahead of the IO buffer wake" v2 (Jake Steinman, intel-gfx, Message-ID `20260903131724.49496-1-j@metarealtyinc.ca`, not merged). On the LG `00:22:b9` panel the spec formulas give fast wake equal to IO buffer wake (11 and 11 lines at 3200x2000@120), and every ALPM link wake then fails with a Link CRC error (70 of 71 polls). Fast wake above IO wake gives 0 of 71. v1 was generic; Intel (Jouni Högander) asked for a panel quirk, hence v2.
- `300.2` is 0020, 0029 and the quirk as **0034**, without 0028, so Panel Replay stays off through the upstream quirk and the display runs PSR2.
- Result: 0 PSR idle timeouts, DSB poll errors and underruns (hundreds before). But PSR2 selective updates then misbehave exactly as the patch author predicted: UI glitches and a screen that feels frozen.
- `xe.enable_psr2_sel_fetch=0` fixes that. On display version 20 and later PSR2 needs selective fetch, so this ends up as PSR1 (`PSR mode: PSR1 enabled`, status `SRDENT`). PSR1 does not use ALPM, so the quirk is inactive there but harmless.

</details>

## Secure Boot

`dell-xps-ptl-config` ships `10-sign-dellptl.install`, a kernel-install plugin that runs before `20-grub.install`. It removes every signature from `vmlinuz` with `sbattach --remove` and signs it again with the akmods key. Kernel modules are signed during the kernel build with a temporary key built into that kernel, so only `vmlinuz` needs the MOK key. akmods signs the out-of-tree modules with the same akmods key.

<details>
<summary>Why strip the signatures first</summary>

Local Fedora kernel builds come signed with the untrusted "Red Hat Test Certifying CA" (`signkernel 0`). `sbsign` adds a second signature after it, and some shim versions only check the first one.

</details>

## Camera (IPU7)

Hardware: IPU7.5 (`8086:b05d`) and an OV08X40 behind the Intel CVS vision chip (`INTC10E1`, USB `06cb:0701`). Stock Fedora loads the staging `intel_ipu7`, `intel_ipu7_isys` and `intel_cvs`, which give raw Bayer nodes only: no image processor (PSYS) and no HAL. RPM Fusion's IPU6 stack does not help either, its HAL asks for `libcamhal/plugins/ipu75xa.so`, which only exists in Intel's IPU7 HAL.

The fix is Omarchy's `intel-ipu7-camera` split into two Fedora specs, an akmod and the userspace, with the same pinned commits and patches. akmod rather than DKMS, the same layout as RPM Fusion's `intel-ipu6-kmod`, and akmods signs with the key that is already enrolled.

<details>
<summary>Problems on the way</summary>

1. **Firmware**: Fedora's `intel-vsc-firmware` already ships `ipu7ptl_fw.bin`, so it is not shipped again.
2. **`intel-vision-drivers`** is not needed, 7.2 has `intel_cvs` in tree.
3. **ACPI build fails on Fedora**: `serdes-pdata.h` includes `media/i2c/lt6911uxe.h` because Fedora enables the mainline `CONFIG_VIDEO_LT6911UXE=m`, and mainline has no such header. Omarchy's kernel does not enable it.
4. Building without ACPI gave a black camera (`intel_ipu7_isys: no subdevice info provided`). The async notifier that binds sensors through `ipu_bridge` and CVS is only compiled with `CONFIG_INTEL_IPU_ACPI`, so `BUILD_INTEL_IPU_ACPI=1` is required.
5. With ACPI back on, an outdated LT6911 path breaks the build (`set_csi2()` called with 3 of 4 arguments). Patch **0101** force-includes a header that undefines the LT6911 Kconfig symbols for this module build only.
6. **The out-of-tree modules did not win**: depmod kept picking `kernel/drivers/staging/media/ipu7/` over `extra/intel-ipu7/`, and the out-of-tree PSYS then hung off the in-tree bus (`deferred probe pending`, no `/dev/ipu7-psys0`). Per-module `override` lines in `depmod.d` were ignored; `search updates extra built-in weak-updates` works.
7. **HAL build**: Fedora's jsoncpp lives in `/usr/include/json`, but the HAL includes `jsoncpp/json/json.h`. A symlink in the build staging directory fixes it.
8. **Bogus Provides**: `gstreamer1.prov` loads the plugin to list its elements, the HAL logs to stdout while probing, and those lines became `Provides`. The generator is turned off for this package.
9. **`v4l2-relayd`**: Fedora's generator starts `v4l2-relayd@<name>` for every `/etc/v4l2-relayd.d/*.conf`, so `ipu7.conf` is enough. Its unit has `LimitNPROC=1` and an empty capability set, which would stop the multithreaded HAL. The drop-in relaxes that, orders it after `camera-init.service` and opens up the device sandbox. The loopback card keeps Fedora's label "Intel MIPI Camera" (`/dev/video50`).

</details>

<details>
<summary>Initramfs regression (2026-10-07)</summary>

After `dell-xps-ptl-config` 1.1 ran `dracut --regenerate-all`, host-only dracut put the IPU7 akmod modules into the initramfs without `intel/ipu/ipu7ptl_fw.bin`. The bus driver probed at about 2 s, before the root filesystem mounted at about 15 s, failed with `-ENOENT` and never retried: no `/dev/ipu7-psys0` and no camera.

Fixed in `intel-ipu7-camera` 1.0.6-3 with `omit_drivers` for the IPU7 modules in `/usr/lib/dracut/dracut.conf.d/90-intel-ipu7-camera.conf`. Live recovery: `echo 0000:00:05.0 > /sys/bus/pci/drivers/intel-ipu7/bind`, then restart `v4l2-relayd@ipu7`. Anything that regenerates the initramfs can pull firmware dependent drivers into early boot.

</details>

<details>
<summary>Camera opens only once, or not at all (2026-10-08)</summary>

Two separate causes, both seen as `PSysDevice: Failed to open psys device Device or resource busy` in the relay log and `intel_ipu7_psys: Runtime PM failed (-16)` in the kernel log. The CVS vision chip (`/sys/bus/i2c/devices/i2c-INTC10E1:00`) and the IPU7 PCI device then show `error` in `power/runtime_status`, and that state only clears with a reboot.

1. **BIOS `HPDSensor=IntelHPD`**: the camera does not open at all, even right after boot. Intel's presence detection keeps the vision chip. The setup screen has no option for it; read and set it from Linux with `dell-wmi-sysman`, it applies on the next boot:

   ```bash
   sudo cat /sys/class/firmware-attributes/dell-wmi-sysman/attributes/HPDSensor/current_value
   echo MSHPD | sudo tee /sys/class/firmware-attributes/dell-wmi-sysman/attributes/HPDSensor/current_value
   ```

2. **The vision chip fails to resume from runtime suspend**: with `MSHPD` the first camera session after boot works, but once the chip suspends it never comes back, so every later open fails. `dell-xps-ptl-config` 1.4 ships a udev rule that keeps only the vision chip awake (`power/control=on`); the IPU7 still suspends and resumes normally. Not yet reported upstream.

Do not use `unbind` on `0000:00:05.0` as a reset: the IPU7 driver crashes in `ipu7_psys_remove` (`ipu7_dma_free`, `find_iova`) and only a reboot recovers.

</details>

## IR camera (Himax HM1092)

The Windows Hello IR sensor is a Himax HM1092 (ACPI `HIMX1092`, `\_SB_.LNK0`). Power, reset and the IR flood LED come from `INT3472:00`, which already exposes `/sys/class/leds/HIMX1092_00::ir_flood_led`. The three `OVTI01AF` entries are disabled BIOS placeholders.

It is **blocked**: the sensor also sits behind the CVS bridge, and no IR frames reach Linux until the bridge passes the IR stream. A working IR camera needs a sensor driver that accepts the 19.2 MHz clock, CVS changes for the IR port (lanes, routing and maybe a handshake), and then the ipu-bridge entry. Only Jake Steinman has reported frames on a DA16260.

<details>
<summary>Upstream state (checked 2026-10-06)</summary>

- `ipu-bridge: Add Himax HM1092 IR sensor` v2 (Jake Steinman): **accepted** in media.git next, for 7.3. Link frequencies 180.48 MHz for Dell (19.2 MHz clock) and 180 MHz for ASUS (24 MHz).
- Two competing sensor drivers, neither reviewed yet:
  - Ramshouriesh R v6 (2026-08-01): devicetree only, 24 MHz only, tested on an ASUS Zenbook A14 (Snapdragon). Rejects the 19.2 MHz clock.
  - Jake Steinman (2026-07-26): ACPI `HIMX1092`, x86 IPU6 and IPU7, **tested on the Dell XPS 16 DA16260**, 648x368. Its 238 register init table was taken from the Windows `hm1092.sys` and checked against a bus capture, which may be a provenance concern upstream.
- The 7.2 CVS driver handles one sink (port 0, RGB) and rejects a lane count mismatch (HM1092 is 1 lane in, 2 out). Intel (Miguel Vadillo, platform-driver-x86, 2026-05-15) agreed that check is wrong and posted a fix; a "secure handshake" on IR port 2 was left open.
- omarchy#8641 (XPS 14): the sensor never answers on I2C; CVS likely controls its power.

</details>

<details>
<summary>What was tried here (patches 0030 to 0033)</summary>

- Patch 0033 adds the `HIMX1092` ACPI ID to the v6 driver and returns `-EPROBE_DEFER` while the fwnode endpoint is missing, like `ov08x40`. v6 as posted only has an OF match table and fails for good if it probes before ipu-bridge creates the endpoint.
- First boot on `300.1`: ACPI match and ipu-bridge work ("Found supported sensor HIMX1092:00"), but probe fails with `external clock 19200000 is not supported`. v6 only has the 24 MHz PLL setup; 19.2 MHz divided by 8 and multiplied by 75 gives the same link.
- With the ipu-bridge entry present but hm1092 failing to probe, the ISYS notifier never completes, so the RGB camera breaks too (`VIDIOC_STREAMON: Broken pipe`). The ipu-bridge entry (0030) was dropped and may only come back together with a working hm1092.
- The IR flood LED has no kernel consumer on purpose; userspace switches the LED around a capture.

</details>

<details>
<summary>Face login</summary>

- Not Howdy: its last stable release was in 2020. The plan is **Gaze** (GunduLabs, Rust, SCRFD, ArcFace and liveness, PAM through `gazed` over D-Bus, TPM sealed templates, a Fedora 45 COPR, `gaze-kde`, OpenVINO and NPU support).
- Gaze would need an 8-bit GREY V4L2 node (relayed from the IPU7 raw10 stream) and a sysfs LED emitter profile for `HIMX1092_00::ir_flood_led`.
- RGB only face login works with the current webcam but is easier to fool with a photo. If used at all: lock screen only, never sudo, SDDM or LUKS, and the password always as a fallback.

</details>

## NPU

Fedora's `intel-npu-driver` is built with `ENABLE_NPU_COMPILER_BUILD=OFF` and ships only `libze_intel_npu.so`, so OpenVINO 2026.4 fails with `Unsupported configuration key: NPU_MAX_TILES`. The package here is Fedora's spec updated to 1.38, built from source, plus an `intel-npu-compiler` subpackage with Intel's prebuilt compiler.

<details>
<summary>Details</summary>

- Intel's 1.38 release ships the compiler prebuilt: `libopenvino_intel_npu_compiler.so` and `_loader.so`.
- Driver and compiler versions have to match: 1.32 loads `libnpu_driver_compiler.so`, 1.38 loads `libopenvino_intel_npu_compiler_loader.so`.
- Fedora's `intel-npu-firmware` works; Intel's newer `vpu_50xx_v1.bin` is not needed.

</details>

## Thermal

`thermald` was inactive after every boot. `dell-xps-ptl-config` adds a drop-in that clears the fallback marker and waits up to 30 s for RAPL, coretemp and `TCPU` before starting. thermald then keeps running and puts every zone into `user_space`. `intel-lpmd`, `tuned` and `tuned-ppd` run fine as they are.

<details>
<summary>Why thermald stopped</summary>

- Fedora's unit already passes `--adaptive`, and Panther Lake (`6:204`) is adaptive only in thermald 2.5.13.
- The first start at boot logs `NO RAPL sysfs present`, `No coretemp sysfs found`, then `Adaptive policy couldn't create any zones`. thermald writes `/run/thermald/ignore_adaptive`, exits, and systemd restarts it in non-adaptive mode, which refuses the CPU (`Unsupported cpu model`).
- Dell's data vault (`INTC10D4:00/data_vault`) is fine. Started after the sensors exist (`SEN1` to `SEN7`, `TCPU`, `TCPU_PCI`, RAPL, coretemp), thermald works.

</details>

## Power profiles

The machine has two platform profile handlers, and KDE's power saver never reached either of them. `dell-xps-ptl-config` ships `xps-ptl-powersave`, `xps-ptl-balanced`, `xps-ptl-balanced-battery` and `xps-ptl-performance` tuned profiles that set each handler by name, and maps tuned-ppd to them.

| KDE profile | Dell thermal mode | SoC slider | Notes |
| --- | --- | --- | --- |
| 🍃 Power saver | quiet | low-power | EPP power, no turbo |
| ⚖️ Balanced | balanced | balanced | |
| 🚀 Performance | performance | performance | EPP performance |

Use KDE's slider or `sudo tuned-adm profile xps-ptl-...`. tuned-ppd has no `powerprofilesctl`, and power-profiles-daemon must not be installed, it conflicts with tuned-ppd.

<details>
<summary>Details</summary>

- `dell-pc` offers cool, quiet, balanced and performance (the BIOS `ThermalManagement` modes Cool, Quiet, Optimized and UltraPerformance, switched at runtime). Intel's "SoC Power Slider" offers low-power, balanced and performance. The legacy `/sys/firmware/acpi/platform_profile` only offers what both share, balanced and performance, so tuned's power saver request reached neither.
- tuned-ppd's original `/etc/tuned/ppd.conf` is kept as `ppd.conf.dell-xps-ptl.orig` and restored on removal.
- In 1.3 tuned-ppd's `sysfs_acpi_monitor` is turned off. It treated legacy platform profile changes it did not make as a firmware hotkey and switched back, undoing every power saver switch 1 ms later. The XPS has no such hotkey.

</details>

## Ambient light

PowerDevil 6.7.5 has no ambient light support, so [plasma-light-and-presence](https://github.com/onuralpszr/plasma-light-and-presence) adds a user service, a System Settings page and a Plasma widget. The light sensor is the ISH ALS through iio-sensor-proxy (`HasAmbientLight`, lux); readings only update while a client holds `ClaimLight`.

<details>
<summary>Pitfalls hit while building it</summary>

- KDE control path: `org.kde.ScreenBrightness/display0` (0 to 10000), `SetBrightness(value, flags)`; flag `0x1` hides the OSD. KDE sends `BrightnessChanged` on the root object and `PropertiesChanged` on the display, and announces unchanged values again, which must not count as user changes.
- iio-sensor-proxy only signals changes, so `LightLevel` is polled every tick; otherwise a smoothed value gets stuck when the room is steady.
- The session's start brightness is not taken as the preference; the learned offset is kept in `~/.local/state/plasma-light-and-presence/state`.
- The ALS reports **bursts of impossible values**: 1 lx in a dark room, but 15 338 and 114 697 lx for 0.5 to 1.5 s at a time, on both ALS devices. It is not the screen's own light, which moves it only 0 to 1 lx from 10 % to 90 %. Fix: 0.5 s sampling, drop anything above 40 000 lx, 30th percentile of a 6 s window, then smoothing.
- Wayland KDE has no `GetSessionIdleTime` and no logind IdleHint, so idle dimming is detected as a sharp drop (50 % or more) and the service waits for the restore.
- Widget: `DBusServiceWatcher.registered` only changes on events, so `NameHasOwner` is checked too. Popups need `Layout.minimumHeight` and `preferredHeight` in the panel or they collapse to the header.
- Icons are original (screen, sensor and light rays), not Dell trademarks, and named after the app id: KDE shortens unknown icon names at each dash inside Breeze first, so a `plasma-...` name turns into the Plasma logo.
- No systemd preset, because a preset enables the unit for every user. Users run `systemctl --user enable --now plasma-light-and-presence`.

</details>

## Presence sensor

Intel "Human Presence v2" (HID `0x200011`, model `HuP v2`, detection type facial) behind the ISH (`ish_ptl_39ceeaf8.bin`, firmware 5.8.1.7783). It is camera based: the Synaptics SVP7500 CVS (`06cb:0701`) runs the vision model on frames from the RGB sensor. Linux exposes it as iio `prox` (`hid-sensor-prox`); its own state field is only visible in the raw HID reports (`plasma-light-and-presence/tools/hpd-diag.py`).

**Not usable on Linux** (BIOS 1.8.2, kernel 7.2.9):

| Condition | Sensor |
| --- | --- |
| sysfs `_raw` reads | presence -1 / 65535 (no data) |
| buffered stream, camera idle | `NOT AVAILABLE`, then silent |
| ov08x40 runtime PM forced on, not streaming | `READY`, then silent |
| test `intel_cvs` with `ICVS_HOST_VISION_SENSING` | no change |
| BIOS `HPDSensor=IntelHPD` (default `MSHPD`) | the same, and the camera stops working; set it back to `MSHPD` (see Camera) |
| camera streaming to an app | about 4 s presence bursts, on motion only |

The CVS only sees frames while the host streams; nothing on Linux sets up its standalone mode, where the chip drives the sensor itself. Four ISH clients have no Linux driver: `1F050626-…`, `A7216DFB-…`, `BB579A2E-…`, `C1CC78B9-…`. This needs Intel or Synaptics and should be reported together with the CVS and IR thread.

## Copilot key

The key sends `LEFTMETA + LEFTSHIFT + F23`. xkeyboard-config 2.48 maps Shift+Super+`<FK23>` to `XF86Assistant`, and Qt 6.11 has no key for it, so KDE cannot bind it. `fkeys:basic_13-24` would fix it but also turns F20 (mic mute) and F21 and F22 (touchpad) into plain F keys. Instead input-remapper maps F23 to F19 and KDE binds Meta+Shift+F19 (`tools/copilot-key`). Upstream, Qt needs a `Key_Assistant` for `XF86Assistant`.

## External displays

- Direct HDMI from the laptop: 4K at 60 Hz works.
- USB-C works through DisplayPort Alt Mode. The top refresh rate depends on how many DisplayPort lanes the dock or adapter gives the monitor.
- Example: an Anker USB-C hub (`291a:8383`, VIA Labs hubs, AX88179 Ethernet, NS1081 card reader) runs USB 3 next to DisplayPort, so the monitor gets 2 lanes (about 8.6 to 13 Gbit/s). That is too little for 4K at 60 Hz or 1440p above 120 Hz, so a 1440p 144 Hz monitor went black or flickered at high rates and settled at 60 Hz. USB, Ethernet and the card reader work. Use 60 Hz, 4K at 30 Hz, or a 4 lane or Thunderbolt dock.

## Not hardware problems

- 🎬 **Codecs**: Fedora's `libva-intel-media-driver` has no H.264 or HEVC; RPM Fusion's `intel-media-driver` has them.
- 👆 **Fingerprint**: the DA16260 has no reader (Dell spec page, nothing on USB, I2C or SPI). `06cb:0701` is the CVS camera bridge. The machine has an IR camera for face login instead.
- 📳 **Touchpad haptics**: the touchpad is `2C2F:0033`. Omarchy's `dell-xps-touchpad-haptics` targets a Synaptics part, so it does not apply.
- ⌨️ **Keyboard backlight**: all levels work.

## Still open

- `xe` `[PLANE:135:plane 5A] fault`, also on the stock kernel. It shows up when a camera or video window opens in KWin, likely an overlay plane buffer freed while still on screen. No visible effect so far.
- Brief green flash when the camera opens, because the relay starts before the first ISP frame; a black splash source would hide it.
- thermald fix: confirm over several cold boots.
- Battery: 10 to 15 hours in daily use so far; idle and sleep drain still to measure.
