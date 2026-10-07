<p align="center">
  <img src="docs/assets/logo.png" alt="xps-fedora logo" width="420">
</p>

<h1 align="center">xps-fedora</h1>

<p align="center">
  Fedora on the Dell XPS 16 (DA16260, Intel Panther Lake), with every piece of hardware working.
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/badge/license-Apache%202.0-blue.svg"></a>
  <a href="https://fedoraproject.org"><img alt="Fedora 45" src="https://img.shields.io/badge/Fedora-45-51A2DA?logo=fedora&amp;logoColor=white"></a>
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/"><img alt="COPR intel-ai-stack" src="https://img.shields.io/badge/COPR-intel--ai--stack-294172?logo=fedora&amp;logoColor=white"></a>
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino/"><img alt="OpenVINO build status" src="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino/status_image/last_build.png"></a>
  <img alt="Secure Boot" src="https://img.shields.io/badge/Secure%20Boot-on-2ea44f">
</p>

## About

This repository holds the RPM packages, patches and notes that make Fedora 45 run well on the Dell XPS 16 DA16260 (Core Ultra X7 358H, Arc B390 graphics, Dell subsystem `1028:0dba`) with Secure Boot left on. It started from what [Omarchy](https://github.com/omacom/omarchy-pkgs) ships for the same machine and grew from there: a patched Fedora kernel, the IPU7 camera stack, the NPU driver and compiler, power profiles that reach the Dell thermal modes, ambient light brightness, and a full OpenVINO and llama.cpp stack built for Fedora.

Most of it is not specific to this laptop. The camera, NPU and AI packages should help any Panther Lake or Lunar Lake machine, and the aim is to send as much as possible to Fedora and upstream projects.

## Hardware status

| Component | Stock Fedora 45 | With this repo | How |
|---|---|---|---|
| Display, VRR 20-120 Hz | not detected | working | `kernel` patch, KDE VRR set to Automatic |
| Display, panel self refresh | glitches, link errors | working (PSR1) | `kernel` ALPM quirk and `xe.enable_psr2_sel_fetch=0` |
| Camera (OV08X40 through IPU7) | raw nodes only | working | `intel-ipu7-kmod`, `intel-ipu7-camera` |
| NPU (Intel AI Boost) | no compiler | working | `intel-npu-driver` 1.38 with `intel-npu-compiler` |
| OpenVINO on CPU, GPU and NPU | no NPU plugin | working | `openvino` 2026.4.1 from the COPR |
| llama.cpp on the Arc GPU | CPU only | working | `llama-cpp-vulkan`, `llama-cpp-openvino` |
| Thermal (thermald, Dell DPTF) | stops after boot | working | `dell-xps-ptl-config` |
| Power profiles and Dell thermal modes | power saver never reached | working | `dell-xps-ptl-config` tuned profiles |
| Ambient light brightness | none | working | `xps-ptl-tools`, moving to plasma-sensord |
| Copilot key | unknown key | working | input-remapper preset in `tools/copilot-key` |
| Video decode H.264 and HEVC | VP9 and AV1 only | working | RPM Fusion `intel-media-driver` |
| Audio, Wi-Fi, Bluetooth, touchpad, keyboard light | working | working | stock |
| IR camera (HM1092) and face login | no driver | blocked | the camera bridge does not pass IR frames yet |
| Presence sensor | not usable | blocked | camera based, needs vendor support, see [findings](docs/findings.md) |

## Installing

The AI stack is in a COPR repository:

```bash
sudo dnf copr enable thunderbirdtr/intel-ai-stack
sudo dnf install openvino libopenvino-intel-npu-plugin python3-openvino-genai \
    llama-cpp-vulkan llama-cpp-openvino intel-npu-driver intel-npu-compiler
```

The kernel, camera and system packages are built from this repository for now. [docs/install.md](docs/install.md) covers the Secure Boot key, the install order and how to check that everything works.

## Packages

**Laptop support**

| Package | What it does |
|---|---|
| [`kernel`](packages/kernel) | Fedora kernel with the VRR, ALPM and HM1092 patches, built as `kernel-*.dellptl` |
| [`intel-ipu7-kmod`](packages/intel-ipu7-kmod) | IPU7 camera drivers as an akmod |
| [`intel-ipu7-camera`](packages/intel-ipu7-camera) | Camera HAL, firmware, GStreamer source and the relay service for apps |
| [`intel-npu-driver`](packages/intel-npu-driver) | NPU driver 1.38 and Intel's NPU compiler |
| [`dell-xps-ptl-config`](packages/dell-xps-ptl-config) | thermald fix, kernel signing hook, display option and power profiles |
| [`xps-ptl-tools`](packages/xps-ptl-tools) | Auto brightness service and Plasma widget |

**AI stack** (published in the COPR)

| Package | Version | Notes |
|---|---|---|
| [`openvino`](packages/openvino) | 2026.4.1 | NPU plugin enabled, new GGUF frontend |
| [`openvino-genai`](packages/openvino-genai) | 2026.4.1.0 | also builds OpenVINO Tokenizers |
| [`onnx`](packages/onnx) | 1.22.0 | shared library kept for onnxruntime and Python |
| [`onnxruntime`](packages/onnxruntime) | 1.30.0 | CPU, MIGraphX and OpenVINO variants |
| [`llama-cpp`](packages/llama-cpp) | b11460 | Vulkan, OpenVINO and HIP backends as subpackages |
| [`python-nncf`](packages/python-nncf), [`python-optimum`](packages/python-optimum), [`python-optimum-intel`](packages/python-optimum-intel), [`python-transformers`](packages/python-transformers), [`python-openvino-telemetry`](packages/python-openvino-telemetry) | latest | model export and compression tools |

## Building

```bash
scripts/build-rpm.sh <package>          # quick local build with rpmbuild
scripts/mock-build.sh <package>         # clean build in mock, as COPR does
scripts/build-kernel.sh                 # the patched kernel
scripts/copr-build.sh <package>         # send a package to the COPR
scripts/fedora-rebuild.sh <package>     # rebuild a Fedora package for the COPR
```

`dnf builddep packages/<name>/<name>.spec` installs the build dependencies of a package. Heavy builds such as OpenVINO are best left to COPR; on a laptop, run `tools/build-host/memory-setup.sh` first so the desktop stays responsive.

## Documentation

* [Install guide](docs/install.md)
* [Hardware findings](docs/findings.md): what was broken and how it was fixed
* [Roadmap](docs/roadmap.md)
* [Upstreaming](docs/upstreaming.md): what can go to Fedora, RPM Fusion and upstream
* [COPR](docs/copr.md): build order and project settings
* [Versions](docs/versions.md): what is pinned and why

## Credits

This work stands on the shoulders of many people.

* The Fedora packagers of the kernel, `openvino`, `onnx`, `onnxruntime`, `llama-cpp` and `intel-npu-driver`, whose specs these packages start from.
* The [Omarchy](https://github.com/omacom/omarchy-pkgs) project, whose Panther Lake kernel and camera packages showed the way.
* Intel, for the IPU7 drivers and camera HAL, the NPU driver and compiler, OpenVINO and OpenVINO GenAI.
* Jake Steinman and the linux-media and intel-gfx developers, for the HM1092, Intel CVS and ALPM work on these laptops.
* The [llama.cpp](https://github.com/ggml-org/llama.cpp), [ONNX](https://github.com/onnx/onnx) and [ONNX Runtime](https://github.com/microsoft/onnxruntime) projects.
* [RPM Fusion](https://rpmfusion.org), for the media driver and codecs.
* The logo is by Onuralp SEZER.

## License

The scripts, configuration and documentation in this repository are released under the [Apache License 2.0](LICENSE). Patches and packaged software keep their own licenses, which are listed in each spec file.
