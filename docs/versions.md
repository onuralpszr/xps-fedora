# Versions and update tracking

Checked 2026-10-06.

| Package | Ours | Base / upstream | Up to date? |
|---|---|---|---|
| `kernel` | 7.2.9-300.dellptl | Fedora f45 latest: `kernel-7.2.9-300` | ✅ rebase on each Fedora kernel update |
| `intel-npu-driver` + `intel-npu-compiler` | 1.38.0-0.1.dellptl | intel/linux-npu-driver latest: v1.38.0 (Fedora f45: 1.35.0) | ✅ |
| NPU firmware | Fedora `intel-npu-firmware` 20260916 | Intel 1.38 `vpu_50xx_v1.bin` | ✅ same build (Aug 20 2026, UD202638) |
| IPU7 firmware | Fedora `intel-vsc-firmware` | ipu7-camera-bins | ✅ same files |
| `intel-ipu7-kmod` | ipu7-drivers `a88b190` | upstream `495acc9` (25 commits ahead) | ⚠️ pinned to Omarchy, see below |
| `intel-ipu7-camera` | hal `b1f6ebe`, bins `403c67d`, icamerasrc `4fb31db` | hal `11d8aff` (+28), bins `adf5552` (+6) | ⚠️ pinned to Omarchy, see below |
| `dell-xps-ptl-config` | 1.0 | n/a | ✅ |
| Omarchy reference | `omarchy-pkgs` master | `97925fbc` last IPU7 change | ✅ no newer changes |

## IPU7: why it stays on Omarchy's pins for now

Results of dry-running our patches on the latest upstream:

| Patch | On latest upstream |
|---|---|
| drivers 0004 PSYS register device bus | merged upstream (`ipu7_psys_bus` + `bus_register`), drop it |
| drivers 0005 harden userptr pinning | **not upstream** (`FOLL_FORCE` still there, no `MAX_RW_COUNT` check) and no longer applies, so it needs a rebase (security fix) |
| drivers 0101 hide LT6911 | applies |
| hal 0005 route through Intel CVS bridge | conflicts with upstream `f167239` "Enable ov08x40 CVS for upstream cvs driver" (configured for ipu8 only), so check whether upstream's version covers ipu75xa |
| hal 0006, 0008, 0010, 0011, 0012 | apply |

Bumping means rebasing a security patch and re-testing the camera. Omarchy
maintains these patches, so the plan is to follow their next bump
(`pkgbuilds/intel-ipu7-camera` in omarchy-pkgs) rather than fork them.

## Checking for updates

```bash
# Fedora kernel
git -C work/kernel fetch -q origin && git -C work/kernel log --oneline -3 origin/f45
# NPU driver releases
curl -s https://api.github.com/repos/intel/linux-npu-driver/releases/latest | grep tag_name
# IPU7 upstream vs pins
for r in work/ipu7-src/*; do git -C $r fetch -q origin; echo "$r $(git -C $r rev-list --count HEAD..origin/HEAD) behind"; done
# Omarchy
git -C ~/Github/omarchy-pkgs log --oneline -3 origin/master -- pkgbuilds/intel-ipu7-camera pkgbuilds/linux-ptl
```
