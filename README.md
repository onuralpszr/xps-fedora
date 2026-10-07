<p align="center">
  <img src="docs/assets/logo.png" alt="xps-fedora logo" width="256">
</p>

<h1 align="center">xps-fedora</h1>

<p align="center">
  Fedora on the Dell XPS 16 (DA16260, Intel Panther Lake), with every piece of hardware working.
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/badge/license-Apache%202.0-blue.svg"></a>
  <a href="https://fedoraproject.org"><img alt="Fedora 45" src="https://img.shields.io/badge/Fedora-45-51A2DA?logo=fedora&amp;logoColor=white"></a>
  <a href="https://github.com/onuralpszr/xps-fedora/actions/workflows/check.yml"><img alt="Check" src="https://github.com/onuralpszr/xps-fedora/actions/workflows/check.yml/badge.svg"></a>
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/"><img alt="COPR intel-ai-stack" src="https://img.shields.io/badge/COPR-intel--ai--stack-294172?logo=fedora&amp;logoColor=white"></a>
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/"><img alt="COPR xps-fedora" src="https://img.shields.io/badge/COPR-xps--fedora-294172?logo=fedora&amp;logoColor=white"></a>
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino/"><img alt="OpenVINO build status" src="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino/status_image/last_build.png"></a>
  <img alt="Secure Boot" src="https://img.shields.io/badge/Secure%20Boot-on-2ea44f">
</p>

## About

This repository holds the RPM packages, patches and notes that make Fedora 45 run well on the Dell XPS 16 DA16260 (Core Ultra X7 358H, Arc B390 graphics, Dell subsystem `1028:0dba`) with Secure Boot left on. It started from what [Omarchy](https://github.com/omacom/omarchy-pkgs) ships for the same machine and grew from there: a patched Fedora kernel, the IPU7 camera stack, the NPU driver and compiler, power profiles that reach the Dell thermal modes, ambient light brightness, and a full OpenVINO and llama.cpp stack built for Fedora.

Most of it is not specific to this laptop. The camera, NPU and AI packages should help any Panther Lake or Lunar Lake machine, and the aim is to send as much as possible to Fedora and upstream projects.

## Hardware status

✅ working, ⚠️ partly working, ❌ not working, ⛔ blocked upstream

| Component | Stock Fedora 45 | With this repo | How |
|---|---|---|---|
| Display, VRR 20-120 Hz | ❌ not detected | ✅ | `kernel` patch, KDE VRR set to Automatic |
| Display, panel self refresh | ⚠️ glitches, link errors | ✅ PSR1 | `kernel` ALPM quirk and `xe.enable_psr2_sel_fetch=0` |
| Camera (OV08X40 through IPU7) | ❌ raw nodes only | ✅ | `intel-ipu7-kmod`, `intel-ipu7-camera` |
| NPU (Intel AI Boost) | ❌ no compiler | ✅ | `intel-npu-driver` 1.38 with `intel-npu-compiler` |
| OpenVINO on CPU, GPU and NPU | ⚠️ no NPU plugin | ✅ | `openvino` 2026.4.1 from the COPR |
| llama.cpp on the Arc GPU | ⚠️ CPU only | ✅ | `llama-cpp-vulkan`, `llama-cpp-openvino` |
| Thermal (thermald, Dell DPTF) | ❌ stops after boot | ✅ | `dell-xps-ptl-config` |
| Power profiles and Dell thermal modes | ❌ power saver never reached | ✅ | `dell-xps-ptl-config` tuned profiles |
| Ambient light brightness | ❌ none | ✅ | `xps-ptl-tools`, moving to plasma-sensord |
| Copilot key | ❌ unknown key | ✅ | input-remapper preset in `tools/copilot-key` |
| Video decode H.264 and HEVC | ⚠️ VP9 and AV1 only | ✅ | RPM Fusion `intel-media-driver` |
| External monitor through a USB-C dock | ✅ | ✅ | limited to 60 Hz by the dock's two DP lanes |
| Audio, Wi-Fi, Bluetooth, touchpad, keyboard light | ✅ | ✅ | stock |
| IR camera (HM1092) and face login | ❌ no driver | ⛔ | the camera bridge does not pass IR frames yet |
| Presence sensor | ❌ not usable | ⛔ | camera based, needs vendor support, see [findings](docs/findings.md) |
| Idle battery drain and sleep states | ⚠️ not measured | ⚠️ | measurement still to do |

## Installing

The AI stack is in a COPR repository:

```bash
sudo dnf copr enable thunderbirdtr/intel-ai-stack
sudo dnf install openvino libopenvino-intel-npu-plugin python3-openvino-genai \
    llama-cpp-vulkan llama-cpp-openvino intel-npu-driver intel-npu-compiler
```

The kernel, the IPU7 camera drivers, the system configuration and plasma-sensord are in a second COPR repository, [thunderbirdtr/xps-fedora](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/). The camera userspace (`intel-ipu7-camera`) contains closed libraries, which COPR does not allow, so it is built from this repository. [docs/install.md](docs/install.md) covers the Secure Boot key, the install order and how to check that everything works.

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
* [CI and automatic builds](docs/ci.md): how pushes reach COPR
* [Versions](docs/versions.md): what is pinned and why

## Credits

This project builds on the work of many people. Thank you all.

**Fedora**

* The packagers of [kernel](https://src.fedoraproject.org/rpms/kernel), [openvino](https://src.fedoraproject.org/rpms/openvino), [onnx](https://src.fedoraproject.org/rpms/onnx), [onnxruntime](https://src.fedoraproject.org/rpms/onnxruntime), [llama-cpp](https://src.fedoraproject.org/rpms/llama-cpp) and [intel-npu-driver](https://src.fedoraproject.org/rpms/intel-npu-driver), whose specs the packages here start from.
* [COPR](https://copr.fedorainfracloud.org), [Packit](https://packit.dev) and [mock](https://github.com/rpm-software-management/mock), which build and publish everything.
* [RPM Fusion](https://rpmfusion.org), for `intel-media-driver`, the codecs and `kmodtool`.

**Hardware enablement**

* [Omarchy](https://github.com/omacom/omarchy-pkgs), whose Panther Lake kernel and camera packages showed the way on this laptop.
* Jake Steinman and the [linux-media](https://lore.kernel.org/linux-media/) and [intel-gfx](https://lore.kernel.org/intel-gfx/) developers, for the HM1092 camera driver, the Intel CVS bridge and the ALPM fast wake quirk.
* Intel, for the [IPU7 drivers](https://github.com/intel/ipu7-drivers), [camera HAL](https://github.com/intel/ipu7-camera-hal), [camera binaries](https://github.com/intel/ipu7-camera-bins), [icamerasrc](https://github.com/intel/icamerasrc), the [NPU driver](https://github.com/intel/linux-npu-driver) and [thermald](https://github.com/intel/thermal_daemon).
* [tuned](https://github.com/redhat-performance/tuned), [iio-sensor-proxy](https://gitlab.freedesktop.org/hadess/iio-sensor-proxy) and [input-remapper](https://github.com/sezanzeb/input-remapper).

**AI stack**

* [OpenVINO](https://github.com/openvinotoolkit/openvino), [OpenVINO GenAI](https://github.com/openvinotoolkit/openvino.genai), [OpenVINO Tokenizers](https://github.com/openvinotoolkit/openvino_tokenizers) and [NNCF](https://github.com/openvinotoolkit/nncf).
* [llama.cpp](https://github.com/ggml-org/llama.cpp), [ONNX](https://github.com/onnx/onnx) and [ONNX Runtime](https://github.com/microsoft/onnxruntime).
* Hugging Face, for [Transformers](https://github.com/huggingface/transformers), [Optimum](https://github.com/huggingface/optimum) and [Optimum Intel](https://github.com/huggingface/optimum-intel).

The logo is by [Onuralp SEZER](https://github.com/onuralpszr).

## License

The scripts, configuration and documentation in this repository are released under the [Apache License 2.0](LICENSE). Patches and packaged software keep their own licenses, which are listed in each spec file.
