# Roadmap: full Fedora support for the Dell XPS 16 (Panther Lake)

Goal: every hardware feature of the XPS 16 DA16260 working on Fedora with
Secure Boot on, installable from one repository, automatically rebuilt on
Fedora updates, and pushed upstream so this project can shrink over time.

Principles:
- **Upstream first.** Prefer patches that are merged or posted upstream; keep
  our own patches small, documented, and offered upstream.
- **Fedora-native.** Start from Fedora's specs, use akmods and kernel-install,
  and don't replace Fedora packages unless we must (and only by version, so
  Fedora's own update takes over again).
- **Reversible.** Everything is a package or a documented boot/config option.

## 1. Feature map

Legend: ✅ done · 🟡 partial · ❌ missing · ⛔ blocked upstream

| Area | Hardware | Status | Notes / next step |
|---|---|---|---|
| Kernel | n/a | ✅ | `kernel-*.dellptl` (VRR, ALPM quirk), rebase on each Fedora kernel |
| Display | LG OLED 3200x2000@120, VRR 20-120 | 🟡 | PSR1 via `xe.enable_psr2_sel_fetch=0`; PSR2 SU / Panel Replay ⛔ upstream |
| GPU | Arc B390 (xe) | ✅ | compute, Level Zero, VA-API (H.264/HEVC/VP9/AV1), Vulkan |
| NPU | Intel AI Boost (NPU5) | ✅ | driver + compiler 1.38 |
| RGB camera | OV08X40 via IPU7 + CVS | ✅ | akmod + HAL; cosmetic green flash on open |
| IR camera | HM1092 via CVS | ⛔ | CVS bridge only routes one sensor; secure handshake open |
| Face login | n/a | ⛔ | Gaze once IR works; RGB-only = lock screen at most |
| Presence sensor | ISH "Human Presence v2" (camera based, via CVS) | ⛔ | sensor reports NOT AVAILABLE unless the camera streams; see findings.md |
| Ambient light | 2× ISH ALS (one with colour temp) | ✅ | `xps-ptl-tools` auto-brightness + widget; colour temperature not used yet |
| Thermal | DPTF, 2 fans | ✅ | thermald adaptive (boot-race fix) |
| Dell thermal modes | `dell-pc` handler (= BIOS `ThermalManagement`) | ✅ | KDE slider → `xps-ptl-*` tuned profiles (`dell-xps-ptl-config` 1.3) |
| Power | s2idle, PSR, NVMe APST, runtime PM | 🟡 | s0ix residency and idle drain not yet measured |
| Battery | Dell charge modes | ✅ | 50-90 % custom; `PrimaryBattChargeCfg` via sysman |
| Audio | SoundWire, cs35l56 ×4 | ✅ | speaker tuning vs Windows not compared |
| Input | haptic-free touchpad, Copilot key | ✅ | Copilot → input-remapper F23→F19 |
| Wi-Fi / BT | CNVi | ✅ | stock |
| Firmware | BIOS 1.8.2 via fwupd | ✅ | n/a |
| AI runtime | OpenVINO / GenAI | 🟡 | full stack in a venv; system-wide needs our packages |
| AI tools | optimum-intel, nncf | 🟡 | venv only |
| llama.cpp | Vulkan on Arc | ❌ | Fedora's build is CPU + HIP (AMD) only |
| Monitoring | n/a | 🟡 | tools exist but no single view |

## 2. Maximum configuration (target)

**Display:** VRR Automatic; PSR1 now, PSR2/Panel Replay once fixed upstream;
auto-brightness from ALS; optional adaptive colour temperature.

**Power profiles** (one switch, KDE's power slider via tuned-ppd):

| Profile | tuned | Dell `ThermalManagement` | EPP | Use |
|---|---|---|---|---|
| Power saver | `powersave`/battery | Quiet | `power` | battery, reading, meetings |
| Balanced | `balanced` | Optimized | `balance_*` | default |
| Performance | `throughput-performance` | UltraPerformance | `performance` | builds, games, LLMs on AC |

**AI device policy:**
- **NPU** for always-on/background inference (lowest power): small LLMs,
  embeddings, Whisper, presence/vision models.
- **GPU** for interactive speed: chat models, image generation, llama.cpp.
- **CPU** as fallback.
- Measure: `intel_gpu_top` (GPU W), `intel-npu-smi` (NPU W), RAPL / `turbostat`
  (package W), `power_now` (system W).

**Sensors:** presence → lock on walk-away, wake/dim on approach/attention;
ALS → brightness; fans/temps → one status view.

**Security:** Secure Boot with own MOK (akmods key), signed kernel + kmods,
face login only with IR (never RGB for sudo/login/LUKS), TPM-sealed templates.

## 3. Missing parts, prioritized

**P0: correctness and daily use**
1. Verify `dell-xps-ptl-config` 1.1 after reboot (PSR1 via modprobe.d).
2. s0ix residency check + idle drain on battery.
3. First git commit; push to GitHub.

**P1: the repository**
4. COPR + one-command install (`dell-xps-ptl` meta package).
5. Automation: rebuild kernel on Fedora kernel updates; watch upstreams.
6. `xps-ptl-doctor`: one command that checks everything in this table.

**P2: features with no Linux software yet**
7. Power profiles ↔ Dell `ThermalManagement` (small daemon or tuned plugin).
8. Presence/attention sensor daemon (walk-away lock, dim when not looking).
9. ALS auto-brightness in KDE (iio-sensor-proxy is already running).
10. llama.cpp with Vulkan.
11. OpenVINO system-wide: `openvino` 2026.4 (+NPU plugin, GGUF), tokenizers,
    genai; then Python tools (transformers, optimum, optimum-intel, nncf).

**P3: blocked or upstream**
12. IR camera + Gaze (needs CVS multi-sensor + HM1092 driver upstream; ask
    Jake Steinman).
13. PSR2 selective update / Panel Replay on the LG panel.
14. Upstream reports (see `upstreaming.md`).
15. Camera: black splash instead of green flash; speaker tuning comparison.

## 4. Repository and packages

### COPR projects

COPR only accepts free software, so the proprietary IPU7 imaging libraries
can't go there.

| Repo | Packages |
|---|---|
| **COPR `xps-ptl`** (free) | `kernel` (`.dellptl`), `akmod-intel-ipu7`, `intel-npu-driver` (+`intel-npu-compiler`, Apache-2.0 prebuilt), `dell-xps-ptl-config`, `xps-ptl-tools` (doctor, power-mode bridge, presence daemon), `llama-cpp` (Vulkan), `openvino` / `openvino-tokenizers` / `openvino-genai`, `python3-transformers` / `-optimum` / `-optimum-intel` / `-nncf` (+ small deps), **`dell-xps-ptl`** meta package |
| **Non-free** (self-hosted repo or RPM Fusion nonfree submission) | `intel-ipu7-camera` (bins + HAL + icamerasrc); long term: split like RPM Fusion's IPU6 stack and submit there |
| Users also need | RPM Fusion free + nonfree (`intel-media-driver`, `v4l2-relayd`, `akmod-v4l2loopback`) |

Chroot: `fedora-45-x86_64` (add `fedora-rawhide-x86_64` once stable).

### Meta package `dell-xps-ptl`
Requires our packages + Fedora/RPM Fusion pieces (`intel-compute-runtime`,
`intel-level-zero`, `oneapi-level-zero`, `intel-media-driver`, `intel-lpmd`,
`thermald`, `tuned-ppd`, `iio-sensor-proxy`, `igt-gpu-tools`, `nvtop`,
`powertop`, `lm_sensors`, `input-remapper`), Recommends the AI stack.

### Secure Boot for COPR users
COPR kernels are unsigned for shim. Each user runs `kmodgenca` + `mokutil
--import` once; `dell-xps-ptl-config`'s hook re-signs `*.dellptl*` kernels,
akmods signs the kmods. `docs/install.md` already covers it.

### Repository layout (target)
```
packages/<name>/        spec + patches (one COPR package each)
packages/kernel/        patches + kernel.spec.diff on Fedora dist-git
tools/                  xps-ptl-doctor, power-mode bridge, presence daemon
scripts/                local builds (build-rpm.sh, build-kernel.sh)
.packit.yaml            COPR builds from git
.github/workflows/      rpmlint + mock builds on PRs; upstream watch (cron)
docs/                   install, findings, upstreaming, versions, roadmap
```

### Automation
- **Packit** (`.packit.yaml`): on push to `main`, build changed packages in COPR.
- **Kernel tracking**: scheduled job compares Fedora f45 `kernel` with our
  `fedora_ref`; on a new build, rebases `kernel.spec.diff`, test-applies the
  patches (`build-kernel.sh prep`), opens a PR.
- **Upstream watch**: NPU driver releases, OpenVINO releases, ipu7-* repos,
  linux-media / intel-gfx patchwork for HM1092, CVS, ALPM, PSR, like
  omarchy-pkgs' upstream-watch.
- **Checks**: rpmlint, `rpmspec -P`, mock build per package; on-device
  `xps-ptl-doctor` after updates.

## 5. Phases

| Phase | Content | Effort |
|---|---|---|
| 1 | P0 items, git commit, push to GitHub | hours |
| 2 | COPR (free packages), meta package, Packit, doctor tool | 1-2 days |
| 3 | Power-mode bridge, ALS auto-brightness, llama.cpp Vulkan | 1-2 days |
| 4 | OpenVINO system packages + Python tools | 2-3 days (long builds) |
| 5 | Presence daemon | 1-2 days |
| 6 | IR camera + Gaze, PSR2/Panel Replay | when upstream moves |
