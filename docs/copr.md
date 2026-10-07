# COPR plan

Not set up yet. Notes for when it is.

## Packages and how COPR would build them

| Package               | COPR source type                                                      | Notes                                                                                                                                                                               |
| --------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dell-xps-ptl-config` | SCM (this repo), spec in `packages/dell-xps-ptl-config`               | noarch, trivial                                                                                                                                                                     |
| `intel-npu-driver`    | SCM                                                                   | Source URLs are upstream archives (spectool fetches them)                                                                                                                           |
| `intel-ipu7-kmod`     | SCM                                                                   | akmod; installs build on the user's machine and sign with their akmods key                                                                                                          |
| `intel-ipu7-camera`   | SCM                                                                   | proprietary bins inside; fine for a personal COPR, note it in the description                                                                                                       |
| `kernel`              | SCM from a fork of Fedora's `rpms/kernel` dist-git, branch `dell-ptl` | the spec is Fedora's; `scripts/build-kernel.sh` reproduces the branch. Long build; COPR kernels are unsigned for Secure Boot, so `dell-xps-ptl-config`'s hook re-signs them locally |

## Things to sort out

- **Kernel naming**: the hook signs only `*.dellptl.*` kernels, so keep `buildid .dellptl`.
- **Kernel builds**: COPR timeout and `--without debug/debuginfo/...` flags (`build-kernel.sh` has the list) need a COPR build config or spec defaults.
- **Version tracking**: kernel follows Fedora's f45 updates (rebase the 3 patches); `intel-npu-driver` should step aside when Fedora ships ≥ 1.38 (`Release: 0.x`).
- **Automation**: a GitHub Action / Packit job to rebuild on Fedora kernel updates and to bump pinned commits.
- **Repo priority**: COPR `intel-npu-driver` vs Fedora's. Version ordering handles it as long as ours is newer.

## AI stack (OpenVINO, NPU, ONNX, llama.cpp)

Generic Intel/AI packages, not Dell-specific; candidates for Fedora proper later. Built and tested locally in mock (`fedora-45-x86_64`) with `scripts/mock-build.sh`, which chains packages through `output/repo/` the way COPR chains builds inside one project.

### Build order

Each batch needs the previous ones in the COPR repo first.

| Batch | Package                     | Version    | Notes                                                                                                        |
| ----- | --------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------ |
| 1     | `onnx`                      | 1.22.0     | Fedora: 1.21.0. 1.22 is what OpenVINO 2026.4 and ORT 1.30 pin (not 1.23). Shared libonnx kept (ported patch) |
| 1     | `python-openvino-telemetry` | 2025.2.0   | new, needed by nncf                                                                                          |
| 1     | `python-transformers`       | 5.5.4      | new; optimum-intel 2.2 needs < 5.6                                                                           |
| 2     | `openvino`                  | 2026.4.1   | Fedora: 2026.0.0. NPU plugin enabled, GGUF frontend subpackage                                               |
| 2     | `python-optimum`            | 2.3.0      | new                                                                                                          |
| 2     | `python-nncf`               | 3.4.0      | new                                                                                                          |
| 3     | `openvino-genai`            | 2026.4.1.0 | new; also builds `openvino-tokenizers` + `python3-openvino-tokenizers`                                       |
| 3     | `onnxruntime`               | 1.30.0     | Fedora: 1.26.0; CPU + MIGraphX + OpenVINO EP variants                                                        |
| 3     | `llama-cpp`                 | b11460     | Fedora: b9840; `-vulkan`, `-openvino`, `-hip` backend subpackages                                            |
| 4     | `python-optimum-intel`      | 2.2.0      | new                                                                                                          |
| 4     | dependents of onnxruntime   | Fedora's   | rebuilt unchanged (see below)                                                                                |

`intel-npu-driver` / `intel-npu-compiler` (batch 0, already above) provide the NPU driver and the compiler the OpenVINO NPU plugin uses.

### onnxruntime dependents

onnxruntime renames its symbol version every release (`VERS_1.26.0` to `VERS_1.30.0`), so these Fedora/RPM Fusion packages must be rebuilt in the COPR or dnf refuses the update:

calibre, crow-translate, gstreamer1-plugins-bad-free, monado, pipewire, vcmi (RPM Fusion; the COPR needs RPM Fusion free as an external repo).

On rawhide, python-torch links the system onnx, so it is rebuilt too (Fedora 45 torch carries its own onnx copy and is not affected).

`scripts/fedora-rebuild.sh <pkg>` makes the SRPM: Fedora's spec unchanged, release `<fedora release>.1.ovstack`, one changelog line. Upload those SRPMs to COPR (`copr-cli build <project> output/rebuild/<pkg>/*.src.rpm`). When Fedora updates one of them, rerun the script.

### COPR project settings

- Chroot `fedora-45-x86_64` (the stack is x86_64-only: OpenVINO, intel-npu-driver).
- External repos: RPM Fusion free (for vcmi), nothing else.
- Network during build: off (all sources are Source: URLs).
- Build timeout: OpenVINO and onnxruntime take 1-3 h each; raise the timeout to 10 h.
