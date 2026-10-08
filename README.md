<p align="center">
  <img src="https://raw.githubusercontent.com/onuralpszr/xps-fedora/main/docs/assets/logo.png" alt="xps-fedora logo" width="256">
</p>

<h1 align="center">xps-fedora</h1>

<p align="center">
  Fedora on the Dell XPS 16 (DA16260, Intel Panther Lake), with every piece of hardware working.
</p>

<p align="center">
  <a href="#tested-on"><img alt="Dell XPS 16 DA16260" src="https://img.shields.io/badge/Dell%20XPS%2016-DA16260-007DB8?logo=dell&amp;logoColor=white"></a>
  <a href="#tested-on"><img alt="Intel Panther Lake" src="https://img.shields.io/badge/Intel-Panther%20Lake-0071C5?logo=intel&amp;logoColor=white"></a>
  <a href="https://fedoraproject.org"><img alt="Fedora 45" src="https://img.shields.io/badge/Fedora-45-51A2DA?logo=fedora&amp;logoColor=white"></a>
  <a href="https://kde.org/plasma-desktop/"><img alt="KDE Plasma 6.7" src="https://img.shields.io/badge/KDE%20Plasma-6.7-1D99F3?logo=kde&amp;logoColor=white"></a>
  <a href="packages/openvino"><img alt="OpenVINO 2026.4.1 with NPU" src="https://img.shields.io/badge/OpenVINO-2026.4.1%20with%20NPU-6D28D9?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxOC44NSAxOC44OCI+PHBhdGggZD0iTTEyLjkxMTcgNy45NjY1MkMxMi42Njc1IDguNDY2MTcgMTIuMTY2MyA4LjgxMzY5IDExLjU2MzMgOC44MTM2OUMxMC43MTcyIDguODEzNjkgMTAuMDU4MyA4LjEyNjI5IDEwLjA1ODMgNy4yODU3MkMxMC4wNTgzIDYuNjc4MiAxMC40MDQ4IDYuMTUyMDggMTAuOTE1MSA1LjkwNDhDMTAuNDU4NyA1LjcwNzM4IDkuOTUzOTUgNS41OTc0NyA5LjQxODE3IDUuNTk3NDdDNy4zMDIgNS41OTc0NyA1LjY1NDk3IDcuMzI5OTkgNS42NTQ5NyA5LjQzMTlDNS42NTQ5NyAxMS41MzM4IDcuMzAyNTEgMTMuMjUxNiA5LjQxODE3IDEzLjI1MTZDMTEuNTQ4MSAxMy4yNTE2IDEzLjE5NTYgMTEuNTMzMyAxMy4xOTU2IDkuNDMxOUMxMy4xOTUxIDguOTEzOTMgMTMuMDkzOCA4LjQxOTM2IDEyLjkxMTcgNy45NjY1MloiIGZpbGw9IndoaXRlIi8+PHBhdGggZD0iTTAgOS40MzdDMCA0LjIyNzc1IDQuMjAyODEgMCA5LjQxMjA2IDBDMTQuNjQ2OCAwIDE4Ljg0OTEgNC4yMjc3NSAxOC44NDkxIDkuNDM3QzE4Ljg0OTEgMTQuNjQ2MiAxNC42NDYyIDE4Ljg3NCA5LjQxMjA2IDE4Ljg3NEM0LjIwMjgxIDE4Ljg3NCAwIDE0LjY0NjIgMCA5LjQzN1pNMTYuMTA2IDkuNDM3QzE2LjEwNiA1LjcxMjQ3IDEzLjE4NyAyLjY0MjI4IDkuNDEyMDYgMi42NDIyOEM1LjY2MjYxIDIuNjQyMjggMi43NDMwMiA1LjcxMjQ3IDIuNzQzMDIgOS40MzdDMi43NDMwMiAxMy4xNjE1IDUuNjYyMSAxNi4yMDYzIDkuNDEyMDYgMTYuMjA2M0MxMy4xODcgMTYuMjA2OCAxNi4xMDYgMTMuMTYxNSAxNi4xMDYgOS40MzdaIiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg=="></a>
  <a href="packages/kernel"><img alt="Kernel 7.2.9-300.2.dellptl" src="https://img.shields.io/badge/kernel-7.2.9--300.2.dellptl-FCC624?logo=linux&amp;logoColor=black"></a>
  <img alt="Secure Boot on" src="https://img.shields.io/badge/Secure%20Boot-on-2ea44f">
</p>

<p align="center">
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/"><img alt="COPR xps-fedora" src="https://img.shields.io/badge/COPR-xps--fedora-294172?logo=fedora&amp;logoColor=white"></a>
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/"><img alt="COPR intel-ai-stack" src="https://img.shields.io/badge/COPR-intel--ai--stack-294172?logo=fedora&amp;logoColor=white"></a>
  <a href="https://github.com/onuralpszr/plasma-light-and-presence"><img alt="plasma-light-and-presence" src="https://img.shields.io/badge/plasma--light--and--presence-widget-1D99F3?logo=kde&amp;logoColor=white"></a>
  <a href="https://github.com/onuralpszr/xps-fedora/releases"><img alt="Camera release" src="https://img.shields.io/github/v/release/onuralpszr/xps-fedora?filter=intel-ipu7-camera-*&amp;label=camera&amp;logo=github"></a>
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/package/kernel/"><img alt="Kernel build" src="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/package/kernel/status_image/last_build.png"></a>
  <a href="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino/"><img alt="OpenVINO build" src="https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino/status_image/last_build.png"></a>
  <a href="https://github.com/onuralpszr/xps-fedora/actions/workflows/check.yml"><img alt="Check" src="https://github.com/onuralpszr/xps-fedora/actions/workflows/check.yml/badge.svg"></a>
  <a href="https://github.com/onuralpszr/xps-fedora/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/onuralpszr/xps-fedora"></a>
  <a href="LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/badge/license-Apache%202.0-blue.svg"></a>
</p>

## About

This repository holds the RPM packages, patches and notes that make Fedora 45 run well on the Dell XPS 16 DA16260 (Core Ultra X7 358H, Arc B390 graphics, Dell subsystem `1028:0dba`) with Secure Boot left on. It started from what [Omarchy](https://github.com/omacom/omarchy-pkgs) ships for the same machine and grew from there: a patched Fedora kernel, the IPU7 camera stack, the NPU driver and compiler, power profiles that reach the Dell thermal modes, ambient light brightness, and a full OpenVINO and llama.cpp stack built for Fedora.

Most of it is not specific to this laptop. The camera, NPU and AI packages should help any Panther Lake or Lunar Lake machine, and the aim is to send as much as possible to Fedora and upstream projects.

<p align="center">
  <a href="#hardware-status"><img src="https://raw.githubusercontent.com/onuralpszr/xps-fedora/main/docs/assets/hardware-infographic.png" alt="Dell XPS 16 hardware support on Fedora and KDE Plasma" width="80%"></a>
</p>

## Tested on

| | Part | Details |
| --- | --- | --- |
| 💻 | **Model** | Dell XPS 16 DA16260, board `0VRKYR`, subsystem `1028:0dba`, BIOS 1.8.2 (2026-05-22) |
| 🧠 | **CPU** | Intel Core Ultra X7 358H (Panther Lake H, 16 cores, up to 4.8 GHz) |
| 🎮 | **Graphics** | Intel Arc B390 (`8086:b080`), `xe` driver, Mesa 26.2.4 |
| ⚡ | **NPU** | Intel AI Boost (`8086:b03e`) |
| 🖥️ | **Display** | LG OLED, 3200x2000, 20-120 Hz VRR |
| 📷 | **Camera** | IPU7.5 (`8086:b05d`) with OV08X40 RGB and Himax HM1092 IR, behind the Synaptics SVP7500 vision chip (`06cb:0701`) |
| 🧮 | **Memory** | 32 GB |
| 💾 | **Storage** | SK hynix PVC10 NVMe, 1 TB |
| 📶 | **Wireless** | Intel CNVi Wi-Fi (`8086:e440`) and Bluetooth |
| 🔊 | **Audio** | Intel HD Audio with SOF SoundWire |
| 🖱️ | **Touchpad** | `2C2F:0033` |
| 🔌 | **Ports** | 3 USB-C with Thunderbolt 4 / USB4 |
| 🔋 | **Battery** | BYD, 68.6 Wh |
| 🐧 | **Software** | Fedora 45, KDE Plasma 6.7.5, kernel 7.2.9-300.2.dellptl |

<details>
<summary>📋 Full <code>lspci</code></summary>

```text
00:00.0 Host bridge: Intel Corporation Core Ultra Processors (Series 3) PTL-H12Xe (rev 04)
00:02.0 VGA compatible controller: Intel Corporation Panther Lake [Arc B390] (rev 04)
00:04.0 Signal processing controller: Intel Corporation Core Ultra Processors (Series 3) DTT (rev 04)
00:05.0 Multimedia controller: Intel Corporation Core Ultra Processors (Series 3) IPU (rev 04)
00:06.0 PCI bridge: Intel Corporation Core Ultra Processors (Series 3) PCIe Root Port #9 (rev 01)
00:07.0 PCI bridge: Intel Corporation Core Ultra Processors (Series 3) USB Type-C Subsystem PCIe Root Port #21 (rev 01)
00:07.1 PCI bridge: Intel Corporation Core Ultra Processors (Series 3) USB Type-C Subsystem PCIe Root Port #22 (rev 01)
00:07.2 PCI bridge: Intel Corporation Core Ultra Processors (Series 3) USB Type-C Subsystem PCIe Root Port #23 (rev 01)
00:0a.0 Signal processing controller: Intel Corporation Core Ultra Processors (Series 3) Crashlog and Telemetry (rev 04)
00:0b.0 Processing accelerators: Intel Corporation Core Ultra Processors (Series 3) NPU (rev 04)
00:0d.0 USB controller: Intel Corporation Core Ultra Processors (Series 3) Type-C Subsystem xHCI (rev 01)
00:0d.2 USB controller: Intel Corporation Core Ultra Processors (Series 3) Thunderbolt DMA0 (rev 01)
00:0d.3 USB controller: Intel Corporation Core Ultra Processors (Series 3) Thunderbolt DMA1 (rev 01)
00:12.0 Serial controller: Intel Corporation Core Ultra Processors (Series 3) ISH (rev 01)
00:13.0 Communication controller: Intel Corporation Core Ultra Processors (Series 3) CSME HECI #1 (rev 01)
00:14.0 USB controller: Intel Corporation Core Ultra Processors (Series 3) Standalone xHCI Controller (rev 01)
00:14.2 RAM memory: Intel Corporation Core Ultra Processors (Series 3) Shared SRAM (rev 01)
00:14.3 Network controller: Intel Corporation Core Ultra Processors (Series 3) CNVi Wi-Fi (rev 01)
00:14.7 Bluetooth: Intel Corporation Core Ultra Processors (Series 3) CNVi Bluetooth (rev 01)
00:16.0 Communication controller: Intel Corporation Core Ultra Processors (Series 3) CSME HECI #1 (CSE) (rev 01)
00:18.0 Communication controller: Intel Corporation Core Ultra Processors (Series 3) CSME HECI #1 (rev 01)
00:19.0 Serial bus controller: Intel Corporation Core Ultra Processors (Series 3) I2C #4 (rev 01)
00:19.1 Serial bus controller: Intel Corporation Core Ultra Processors (Series 3) I2C #5 (rev 01)
00:1f.0 ISA bridge: Intel Corporation Core Ultra Processors (Series 3) eSPI (rev 01)
00:1f.3 Audio device: Intel Corporation Core Ultra Processors (Series 3) HD Audio (rev 01)
00:1f.4 SMBus: Intel Corporation Core Ultra Processors (Series 3) SMBus (rev 01)
00:1f.5 Serial bus controller: Intel Corporation Core Ultra Processors (Series 3) SPI (flash) Controller (rev 01)
01:00.0 Non-Volatile memory controller: SK hynix PVC10 NVMe Solid State Drive (DRAM-less)
```

</details>

<details>
<summary>📋 Full <code>lsusb</code></summary>

```text
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Device 002: ID 06cb:0701 Synaptics, Inc. SVP7500
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
```

</details>

## Hardware status

![Working](https://img.shields.io/badge/working-15-2ea44f?style=for-the-badge) ![Blocked](https://img.shields.io/badge/blocked-2-cf222e?style=for-the-badge)

✅ working &nbsp; ⚠️ partly working &nbsp; ❌ not working &nbsp; ⛔ blocked upstream

### 🐧 Kernel

| Component | Stock Fedora 45 | With this repo | How |
| --- | :---: | :---: | --- |
| 🐧 **Fedora kernel 7.2.9 with Panther Lake fixes** | ⚠️ no display and PSR fixes | ✅ | `kernel` 7.2.9-300.2.dellptl from the COPR, Secure Boot stays on |

### 🖥️ Display and graphics

| Component | Stock Fedora 45 | With this repo | How |
| --- | :---: | :---: | --- |
| 🌈 **VRR 20-120 Hz** | ❌ not detected | ✅ | `kernel` patch, KDE VRR set to Automatic |
| ✨ **Panel self refresh** | ⚠️ glitches, link errors | ✅ PSR1 | `kernel` ALPM quirk and `xe.enable_psr2_sel_fetch=0` |
| 🎬 **Video decode H.264 and HEVC** | ⚠️ VP9 and AV1 only | ✅ | RPM Fusion `intel-media-driver` |
| 🔌 **External monitor over USB-C** | ✅ | ✅ | works; the top refresh rate depends on the dock or adapter, see [findings](docs/findings.md) |

### 📷 Camera

| Component | Stock Fedora 45 | With this repo | How |
| --- | :---: | :---: | --- |
| 🎥 **Camera (OV08X40 through IPU7)** | ❌ raw nodes only | ✅ | `intel-ipu7-kmod`, `intel-ipu7-camera` |
| 🙂 **IR camera (HM1092) and face login** | ❌ no driver | ⛔ | the camera bridge does not pass IR frames yet |

### 🧠 AI and NPU

| Component | Stock Fedora 45 | With this repo | How |
| --- | :---: | :---: | --- |
| ⚡ **NPU (Intel AI Boost)** | ❌ no compiler | ✅ | `intel-npu-driver` 1.38 with `intel-npu-compiler` |
| 🧩 **OpenVINO on CPU, GPU and NPU** | ⚠️ no NPU plugin | ✅ | `openvino` 2026.4.1 from the COPR |
| 🦙 **llama.cpp on the Arc GPU** | ⚠️ CPU only | ✅ | `llama-cpp-vulkan`, `llama-cpp-openvino` |

### 🌡️ Power and thermal

| Component | Stock Fedora 45 | With this repo | How |
| --- | :---: | :---: | --- |
| ❄️ **Thermal (thermald, Dell DPTF)** | ❌ stops after boot | ✅ | `dell-xps-ptl-config` |
| 🎚️ **Power profiles and Dell thermal modes** | ❌ power saver never reached | ✅ | `dell-xps-ptl-config` tuned profiles |
| 🔋 **Battery life** | ⚠️ not measured | ✅ 10-15 h | 10 to 15 hours in daily use so far; idle and sleep drain still to measure |

### ⌨️ Input and sensors

| Component | Stock Fedora 45 | With this repo | How |
| --- | :---: | :---: | --- |
| 💡 **Ambient light brightness** | ❌ none | ✅ | [plasma-light-and-presence](https://github.com/onuralpszr/plasma-light-and-presence) |
| 🤖 **Copilot key** | ❌ unknown key | ✅ | input-remapper preset in `tools/copilot-key` |
| 👤 **Presence sensor** | ❌ not usable | ⛔ | camera based, needs vendor support, see [findings](docs/findings.md) |
| 🎧 **Audio, Wi-Fi, Bluetooth, touchpad, keyboard light** | ✅ | ✅ | stock |

## Installing

Everything comes from three places: two COPR repositories for the open packages, RPM Fusion for codecs and the camera relay, and a GitHub release for the camera userspace, which contains Intel's closed libraries and therefore cannot live in COPR.

| | Source | What it gives you |
| --- | --- | --- |
| 🧩 | [thunderbirdtr/xps-fedora](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/) | kernel, IPU7 camera drivers, system configuration, plasma-light-and-presence |
| 🧠 | [thunderbirdtr/intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | NPU driver and compiler, OpenVINO, ONNX Runtime, llama.cpp, Python model tools |
| 📦 | [RPM Fusion](https://rpmfusion.org/) free and nonfree | H.264 and HEVC decode, `v4l2-relayd`, `v4l2loopback` |
| 📷 | [GitHub releases](https://github.com/onuralpszr/xps-fedora/releases) | `intel-ipu7-camera` (camera HAL and Intel imaging libraries) |

### ⚡ One line

Adds every repository, sets up the Secure Boot key and installs everything. `mokutil` asks for a one-time password; enroll the key in MOK Manager on the next boot.

```bash
sudo dnf install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm && sudo dnf copr enable -y thunderbirdtr/xps-fedora && sudo dnf copr enable -y thunderbirdtr/intel-ai-stack && sudo dnf install -y akmods sbsigntools mokutil && sudo kmodgenca -a && sudo mokutil --import /etc/pki/akmods/certs/public_key.der && sudo dnf install -y dell-xps-ptl-config && sudo dnf install -y kernel akmod-intel-ipu7 plasma-light-and-presence https://github.com/onuralpszr/xps-fedora/releases/download/intel-ipu7-camera-1.0.6-4.dellptl/intel-ipu7-camera-1.0.6-4.dellptl.fc45.x86_64.rpm intel-npu-driver intel-npu-compiler openvino libopenvino-intel-npu-plugin python3-openvino-genai llama-cpp-vulkan llama-cpp-openvino && sudo dnf swap -y libva-intel-media-driver intel-media-driver --allowerasing && sudo reboot
```

### 🚀 Everything, step by step

```bash
# 1. Repositories
sudo dnf install \
  https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf copr enable thunderbirdtr/xps-fedora
sudo dnf copr enable thunderbirdtr/intel-ai-stack

# 2. Secure Boot key, once (reboot and enroll it in MOK Manager afterwards)
sudo dnf install akmods sbsigntools mokutil
sudo kmodgenca -a
sudo mokutil --import /etc/pki/akmods/certs/public_key.der

# 3. Laptop support (configuration first, so its signing hook is ready for the kernel)
sudo dnf install dell-xps-ptl-config
sudo dnf install kernel akmod-intel-ipu7 plasma-light-and-presence
sudo dnf swap libva-intel-media-driver intel-media-driver --allowerasing

# 4. Camera
sudo dnf install https://github.com/onuralpszr/xps-fedora/releases/download/intel-ipu7-camera-1.0.6-4.dellptl/intel-ipu7-camera-1.0.6-4.dellptl.fc45.x86_64.rpm

# 5. NPU and AI stack
sudo dnf install intel-npu-driver intel-npu-compiler openvino libopenvino-intel-npu-plugin \
  python3-openvino-genai llama-cpp-vulkan llama-cpp-openvino

sudo reboot
```

### 🧱 Or one set at a time

<details>
<summary>🐧 <b>Kernel and system configuration</b>: display fixes, thermald, power profiles, kernel signing</summary>

`dell-xps-ptl-config` signs every new kernel with the akmods key, so set up the Secure Boot key first and install it before the kernel.

```bash
sudo dnf copr enable thunderbirdtr/xps-fedora
sudo dnf install akmods sbsigntools mokutil
sudo kmodgenca -a
sudo mokutil --import /etc/pki/akmods/certs/public_key.der   # reboot and enroll
sudo dnf install dell-xps-ptl-config
sudo dnf install kernel
```

</details>

<details>
<summary>📷 <b>Camera</b>: IPU7 drivers, HAL and the relay that shows up as a normal webcam</summary>

Needs RPM Fusion for `v4l2-relayd` and `v4l2loopback`. Remove RPM Fusion's IPU6 stack first if it is installed, its `libcamhal` and `icamerasrc` clash with the IPU7 ones.

```bash
sudo dnf remove akmod-intel-ipu6 'kmod-intel-ipu6*' ipu6-camera-hal ipu6-camera-bins gstreamer1-plugins-icamerasrc
sudo dnf install akmod-intel-ipu7
sudo dnf install https://github.com/onuralpszr/xps-fedora/releases/download/intel-ipu7-camera-1.0.6-4.dellptl/intel-ipu7-camera-1.0.6-4.dellptl.fc45.x86_64.rpm
```

The camera appears as "Intel MIPI Camera" after a reboot.

</details>

<details>
<summary>🎬 <b>Video decode</b>: H.264 and HEVC on the Arc GPU</summary>

```bash
sudo dnf swap libva-intel-media-driver intel-media-driver --allowerasing
```

</details>

<details>
<summary>💡 <b>Ambient light brightness</b>: plasma-light-and-presence</summary>

```bash
sudo dnf install plasma-light-and-presence
systemctl --user enable --now plasma-light-and-presence
```

Settings are under System Settings, and a widget can be added to the panel.

</details>

<details>
<summary>⚡ <b>NPU</b>: driver and Intel's compiler</summary>

```bash
sudo dnf copr enable thunderbirdtr/intel-ai-stack
sudo dnf install intel-npu-driver intel-npu-compiler
```

</details>

<details>
<summary>🧠 <b>AI stack</b>: OpenVINO, GenAI, ONNX Runtime, llama.cpp and the Python model tools</summary>

```bash
# OpenVINO with the NPU plugin, GenAI and tokenizers
sudo dnf install openvino libopenvino-intel-npu-plugin python3-openvino python3-openvino-genai python3-openvino-tokenizers
# llama.cpp with the Arc GPU through Vulkan or OpenVINO
sudo dnf install llama-cpp-vulkan llama-cpp-openvino
# Speech to text with whisper.cpp on the Arc GPU
sudo dnf install whisper-cpp llama-cpp-vulkan
# ONNX Runtime with the OpenVINO execution provider
sudo dnf install onnxruntime-openvino python3-onnxruntime-openvino
# Convert and compress your own models
sudo dnf install python3-optimum-intel python3-nncf python3-transformers python3-torch
```

</details>

[docs/install.md](docs/install.md) has the details: the MOK enrollment screens, the install order and the commands to check that everything works after the reboot.

## Good to know

| | Topic | What to expect |
| --- | --- | --- |
| 🐧 | **Fedora kernel updates** | The `.dellptl` kernel is Fedora's kernel with a few patches. When Fedora ships a newer kernel, a daily [watch](.github/workflows/upstream-watch.yml) rebuilds ours on top of it, usually the same day. If Fedora's kernel lands first, the display fixes are missing until the rebuild arrives; pick the `.dellptl` entry in the boot menu, or make it the default as shown in the [install guide](docs/install.md#going-back-to-the-dellptl-kernel). |
| 🔁 | **Rebuilt Fedora packages** | pipewire, calibre, monado, crow-translate, gstreamer1-plugins-bad-free and vcmi are rebuilt in the intel-ai-stack COPR against onnxruntime 1.30. When Fedora updates one of them, dnf may hold the update back or offer to swap onnxruntime until the same daily watch rebuilds it. Answer no to a swap that removes `onnxruntime` 1.30 and try again a day later. |
| 📷 | **Camera updates** | `intel-ipu7-camera` comes from a GitHub release, not a repository, so `dnf upgrade` does not see new versions. Watch the [releases](https://github.com/onuralpszr/xps-fedora/releases) or the camera badge at the top. It moves to RPM Fusion once it is accepted there. |
| 🎥 | **Camera does not open** | Check the BIOS presence setting, which the setup screen does not show: `sudo cat /sys/class/firmware-attributes/dell-wmi-sysman/attributes/HPDSensor/current_value` must say `MSHPD`, not `IntelHPD`. Set it with `echo MSHPD \| sudo tee` to the same file and reboot. If the camera opens only once per boot, update `dell-xps-ptl-config` to 1.4 or newer. See [findings](docs/findings.md#camera-ipu7). |
| 🔐 | **Secure Boot** | Every new `.dellptl` kernel and every IPU7 module rebuild is signed with your akmods key automatically. If the camera disappears after a kernel update, run `sudo akmods --force` and reboot. |
| 🦙 | **llama.cpp and ollama** | The COPR's llama.cpp ships a newer `libggml` than Fedora's ollama expects, so the two may conflict; do not install both from these repositories yet. Install the backend you want explicitly (`llama-cpp-vulkan` or `llama-cpp-openvino`); plain `llama-cpp` is CPU only. |

## Packages

**Laptop support**

| Package                                                                                | What it does                                                                              |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [`kernel`](packages/kernel)                                                            | Fedora kernel with the VRR, ALPM and HM1092 patches, built as `kernel-*.dellptl`          |
| [`intel-ipu7-kmod`](packages/intel-ipu7-kmod)                                          | IPU7 camera drivers as an akmod                                                           |
| [`intel-ipu7-camera`](packages/intel-ipu7-camera)                                      | Camera HAL, firmware, GStreamer source and the relay service for apps                     |
| [`intel-npu-driver`](packages/intel-npu-driver)                                        | NPU driver 1.38 and Intel's NPU compiler                                                  |
| [`dell-xps-ptl-config`](packages/dell-xps-ptl-config)                                  | thermald fix, kernel signing hook, display option and power profiles                      |
| [`plasma-light-and-presence`](https://github.com/onuralpszr/plasma-light-and-presence) | Ambient light brightness with a System Settings page and a Plasma widget (own repository) |

**AI stack** (published in the COPR)

| Package                                                                                                                                                                                                                                                               | Version    | Notes                                            |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------ |
| [`openvino`](packages/openvino)                                                                                                                                                                                                                                       | 2026.4.1   | NPU plugin enabled, new GGUF frontend            |
| [`openvino-genai`](packages/openvino-genai)                                                                                                                                                                                                                           | 2026.4.1.0 | also builds OpenVINO Tokenizers                  |
| [`onnx`](packages/onnx)                                                                                                                                                                                                                                               | 1.22.0     | shared library kept for onnxruntime and Python   |
| [`onnxruntime`](packages/onnxruntime)                                                                                                                                                                                                                                 | 1.30.0     | CPU, MIGraphX and OpenVINO variants              |
| [`llama-cpp`](packages/llama-cpp)                                                                                                                                                                                                                                     | b11460     | Vulkan, OpenVINO and HIP backends as subpackages |
| [`whisper-cpp`](packages/whisper-cpp) | 1.9.5 | speech to text, shares ggml and its GPU backends with llama-cpp |
| [`python-nncf`](packages/python-nncf), [`python-optimum`](packages/python-optimum), [`python-optimum-intel`](packages/python-optimum-intel), [`python-transformers`](packages/python-transformers), [`python-openvino-telemetry`](packages/python-openvino-telemetry) | latest     | model export and compression tools               |

## Build status

Live status of the last COPR build of each package.

| Package | COPR project | Status | What it is |
| --- | --- | --- | --- |
| `kernel` | [xps-fedora](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/) | [![kernel](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/package/kernel/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/package/kernel/) | Fedora kernel with the XPS 16 patches |
| `intel-ipu7-kmod` | [xps-fedora](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/) | [![intel-ipu7-kmod](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/package/intel-ipu7-kmod/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/package/intel-ipu7-kmod/) | IPU7 camera drivers (akmod) |
| `intel-ipu7-camera` | [GitHub release](https://github.com/onuralpszr/xps-fedora/releases/tag/intel-ipu7-camera-1.0.6-4.dellptl) | [![intel-ipu7-camera](https://img.shields.io/github/v/release/onuralpszr/xps-fedora?filter=intel-ipu7-camera-*&label=release)](https://github.com/onuralpszr/xps-fedora/releases/tag/intel-ipu7-camera-1.0.6-4.dellptl) | IPU7 camera HAL, firmware and relay service |
| `dell-xps-ptl-config` | [xps-fedora](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/) | [![dell-xps-ptl-config](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/package/dell-xps-ptl-config/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/package/dell-xps-ptl-config/) | thermald, power profiles, kernel signing |
| `plasma-light-and-presence` | [plasma-light-and-presence](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/plasma-light-and-presence/) | [![plasma-light-and-presence](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/plasma-light-and-presence/package/plasma-light-and-presence/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/plasma-light-and-presence/package/plasma-light-and-presence/) | ambient light brightness for Plasma |
| `intel-npu-driver` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![intel-npu-driver](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/intel-npu-driver/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/intel-npu-driver/) | NPU driver and compiler |
| `openvino` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![openvino](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino/) | OpenVINO with the NPU plugin |
| `openvino-genai` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![openvino-genai](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino-genai/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/openvino-genai/) | OpenVINO GenAI and Tokenizers |
| `onnx` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![onnx](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/onnx/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/onnx/) | ONNX |
| `onnxruntime` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![onnxruntime](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/onnxruntime/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/onnxruntime/) | ONNX Runtime with the OpenVINO EP |
| `llama-cpp` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![llama-cpp](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/llama-cpp/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/llama-cpp/) | llama.cpp with Vulkan and OpenVINO |
| `python-transformers` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![python-transformers](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-transformers/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-transformers/) | Hugging Face Transformers |
| `python-optimum` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![python-optimum](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-optimum/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-optimum/) | Hugging Face Optimum |
| `python-optimum-intel` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![python-optimum-intel](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-optimum-intel/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-optimum-intel/) | Optimum Intel |
| `python-nncf` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![python-nncf](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-nncf/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-nncf/) | NNCF |
| `python-openvino-telemetry` | [intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | [![python-openvino-telemetry](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-openvino-telemetry/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-openvino-telemetry/) | OpenVINO telemetry |

`intel-ipu7-camera` contains closed Intel libraries, which COPR does not allow. Test builds are attached to [GitHub releases](https://github.com/onuralpszr/xps-fedora/releases), and a submission to RPM Fusion nonfree is planned.

### Rebuilt Fedora packages

The newer onnx and onnxruntime change their library versions, so these Fedora and RPM Fusion packages are rebuilt unchanged in `intel-ai-stack`, with a `.ovstack` release suffix.

| Package                       | Chroots            | Why                            | Status                                                                                                                                                                                                                                                                            |
| ----------------------------- | ------------------ | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `calibre`                     | Fedora 45, rawhide | links onnxruntime              | [![calibre](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/calibre/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/calibre/)                                                             |
| `crow-translate`              | Fedora 45, rawhide | links onnxruntime              | [![crow-translate](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/crow-translate/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/crow-translate/)                                        |
| `gstreamer1-plugins-bad-free` | Fedora 45, rawhide | links onnxruntime              | [![gstreamer1-plugins-bad-free](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/gstreamer1-plugins-bad-free/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/gstreamer1-plugins-bad-free/) |
| `monado`                      | Fedora 45, rawhide | links onnxruntime              | [![monado](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/monado/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/monado/)                                                                |
| `pipewire`                    | Fedora 45, rawhide | links onnxruntime              | [![pipewire](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/pipewire/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/pipewire/)                                                          |
| `vcmi`                        | Fedora 45, rawhide | links onnxruntime (RPM Fusion) | [![vcmi](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/vcmi/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/vcmi/)                                                                      |
| `python-torch`                | rawhide            | links onnx                     | [![python-torch](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-torch/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/package/python-torch/)                                              |

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

- [Install guide](docs/install.md)
- [Hardware findings](docs/findings.md): what was broken and how it was fixed
- [Local AI benchmarks](docs/benchmarks.md): llama.cpp, OpenVINO GenAI, whisper.cpp and embeddings on CPU, GPU and NPU
- [Roadmap](docs/roadmap.md)
- [Upstreaming](docs/upstreaming.md): what can go to Fedora, RPM Fusion and upstream
- [Fedora to-do](docs/fedora-todo.md): the steps to get the packages into Fedora
- [COPR](docs/copr.md): build order and project settings
- [CI and automatic builds](docs/ci.md): how pushes reach COPR
- [Versions](docs/versions.md): what is pinned and why

## Credits

This project builds on the work of many people. Thank you all.

**Fedora**

- The packagers of [kernel](https://src.fedoraproject.org/rpms/kernel), [openvino](https://src.fedoraproject.org/rpms/openvino), [onnx](https://src.fedoraproject.org/rpms/onnx), [onnxruntime](https://src.fedoraproject.org/rpms/onnxruntime), [llama-cpp](https://src.fedoraproject.org/rpms/llama-cpp) and [intel-npu-driver](https://src.fedoraproject.org/rpms/intel-npu-driver), whose specs the packages here start from.
- [COPR](https://copr.fedorainfracloud.org), [Packit](https://packit.dev) and [mock](https://github.com/rpm-software-management/mock), which build and publish everything.
- [RPM Fusion](https://rpmfusion.org), for `intel-media-driver`, the codecs and `kmodtool`.

**Hardware enablement**

- [Omarchy](https://github.com/omacom/omarchy-pkgs), whose Panther Lake kernel and camera packages showed the way on this laptop.
- Jake Steinman and the [linux-media](https://lore.kernel.org/linux-media/) and [intel-gfx](https://lore.kernel.org/intel-gfx/) developers, for the HM1092 camera driver, the Intel CVS bridge and the ALPM fast wake quirk.
- Intel, for the [IPU7 drivers](https://github.com/intel/ipu7-drivers), [camera HAL](https://github.com/intel/ipu7-camera-hal), [camera binaries](https://github.com/intel/ipu7-camera-bins), [icamerasrc](https://github.com/intel/icamerasrc), the [NPU driver](https://github.com/intel/linux-npu-driver) and [thermald](https://github.com/intel/thermal_daemon).
- [tuned](https://github.com/redhat-performance/tuned), [iio-sensor-proxy](https://gitlab.freedesktop.org/hadess/iio-sensor-proxy) and [input-remapper](https://github.com/sezanzeb/input-remapper).

**AI stack**

- [OpenVINO](https://github.com/openvinotoolkit/openvino), [OpenVINO GenAI](https://github.com/openvinotoolkit/openvino.genai), [OpenVINO Tokenizers](https://github.com/openvinotoolkit/openvino_tokenizers) and [NNCF](https://github.com/openvinotoolkit/nncf).
- [llama.cpp](https://github.com/ggml-org/llama.cpp), [ONNX](https://github.com/onnx/onnx) and [ONNX Runtime](https://github.com/microsoft/onnxruntime).
- Hugging Face, for [Transformers](https://github.com/huggingface/transformers), [Optimum](https://github.com/huggingface/optimum) and [Optimum Intel](https://github.com/huggingface/optimum-intel).

The logo is by [Onuralp SEZER](https://github.com/onuralpszr).

## License

The scripts, configuration and documentation in this repository are released under the [Apache License 2.0](LICENSE). Patches and packaged software keep their own licenses, which are listed in each spec file.
