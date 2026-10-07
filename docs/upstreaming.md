# Upstreaming

Everything here should eventually come from Fedora, RPM Fusion or upstream,
so this repo only bridges the gap. Grouped by where each piece belongs.

## Upstream projects

| Item | Project | Notes |
|---|---|---|
| Patches 0020, 0028, 0029 | `drm-intel` / `dri-devel` | Intel (Gaggery Tsai) and Dell (Spencer Bull) authored, already headed upstream. 0028 refs drm/xe work item 7521. |
| thermald boot race | intel/thermal_daemon | adaptive-only CPUs should wait for/retry the PSVT sensors instead of writing `ignore_adaptive` and exiting; the non-adaptive fallback then refuses the CPU |
| LT6911 vs ACPI build (patch 0101) | intel/ipu7-drivers | fix the `set_csi2()` call in `populate_dummy()` and don't depend on an lt6911uxe header mainline doesn't have |
| PSYS driver | intel/ipu7-drivers, then mainline | once PSYS is in mainline the akmod can go |
| HM1092 ACPI support (patch 0033) | linux-media, as a reply to the v6 series | ACPI match `HIMX1092` + `-EPROBE_DEFER`; needed for every Intel laptop with this sensor |
| `plane 5A fault` | drm/xe issues | include dmesg, Panther Lake / Arc B390, XPS 16, KWin, "camera/video window opens" |
| depmod `override` ignored | kmod | confirm with a minimal repro first |
| Copilot key unbindable in KDE | Qt (qtbase) | no `Qt::Key` for `XF86Assistant`, which xkeyboard-config ≥ 2.4x emits for Shift+Super+F23 |

## Fedora

| Package | Request | Notes |
|---|---|---|
| `intel-npu-driver` | update to ≥ 1.38 and ship the NPU compiler | `packages/intel-npu-driver` is the f45 spec + version bump + compiler subpackage; maintained by Intel folks, so bugzilla or a dist-git PR. The prebuilt binary may not pass Fedora review; building `openvinotoolkit/npu_compiler` from source is the proper fix. |
| `openvino` | NPU plugin, `openvino-genai`, `openvino-tokenizers` | Fedora 2026.0 ships CPU/GPU plugins but `-DENABLE_INTEL_NPU=OFF` (no reason given in the Intel-maintained spec) and no GenAI |
| `thermald` | drop-in or upstream fix for the boot race | until upstream fixes it |
| `kernel` | backports of 0020/0028/0029 | only after they're in a maintainer tree |

## RPM Fusion

| Package | Like | Notes |
|---|---|---|
| `intel-ipu7-kmod` | `intel-ipu6-kmod` | same kmodtool layout, already in that form |
| `ipu7-camera-bins` | `ipu6-camera-bins` | nonfree, Intel's prebuilt imaging libs |
| `ipu7-camera-hal` | `ipu6-camera-hal` | nonfree (links the bins); Omarchy's 6 patches for OV08X40/CVS |
| `gstreamer1-plugins-icamerasrc` | existing package | today built against the IPU6 HAL only; needs an IPU7 build |
| `v4l2-relayd` | existing package | IPU7 config + unit relaxations (`LimitNPROC`, sandbox) |

Our `intel-ipu7-camera` bundles bins + HAL + icamerasrc + config in one
package for simplicity. For RPM Fusion it should be split the way the IPU6
stack is.
