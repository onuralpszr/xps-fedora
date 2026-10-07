# Installing

The step by step guide. The [README](../README.md#installing) has the short version with every command in one block.

## 1. 📦 Repositories

RPM Fusion free and nonfree provide `intel-media-driver`, `v4l2-relayd` and `v4l2loopback`. The two COPR repositories provide everything else except the camera userspace.

```bash
sudo dnf install \
  https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf copr enable thunderbirdtr/xps-fedora
sudo dnf copr enable thunderbirdtr/intel-ai-stack
```

Remove RPM Fusion's IPU6 camera stack if it was installed. Its `libcamhal` and `icamerasrc` conflict with the IPU7 ones:

```bash
sudo dnf remove akmod-intel-ipu6 'kmod-intel-ipu6*' ipu6-camera-hal \
  ipu6-camera-bins gstreamer1-plugins-icamerasrc
```

## 2. 🔐 Secure Boot key (once)

The kernel from the COPR and the IPU7 kernel modules are not signed by Fedora, so they are signed on your machine with the akmods key, which shim has to trust. Secure Boot stays on.

```bash
sudo dnf install akmods sbsigntools mokutil
sudo kmodgenca -a                       # creates /etc/pki/akmods/{certs,private}
sudo mokutil --import /etc/pki/akmods/certs/public_key.der
sudo reboot
```

On the blue MOK Manager screen pick Enroll MOK, Continue, Yes, type the password you just set, then Reboot. Check it afterwards:

```bash
mokutil --list-enrolled | grep Subject  # the akmods key is listed
```

## 3. 🐧 Kernel and configuration

Install `dell-xps-ptl-config` first. It brings the signing hook, so the kernel is signed with the akmods key as it installs.

```bash
sudo dnf install dell-xps-ptl-config
sudo dnf install kernel
```

The `.dellptl` kernel sorts above Fedora's kernel of the same version. When Fedora ships a newer kernel, dnf will prefer it until the COPR catches up; the older `.dellptl` kernel stays in the boot menu.

## 4. 📷 Camera

```bash
sudo dnf install akmod-intel-ipu7
sudo dnf install https://github.com/onuralpszr/xps-fedora/releases/download/intel-ipu7-camera-1.0.6-4.dellptl/intel-ipu7-camera-1.0.6-4.dellptl.fc45.x86_64.rpm
```

akmods builds the IPU7 modules for every installed kernel on the next boot. To build them right away:

```bash
sudo akmods --force
```

## 5. 🎬 Video decode and 💡 ambient light

```bash
sudo dnf swap libva-intel-media-driver intel-media-driver --allowerasing
sudo dnf install plasma-light-and-presence
systemctl --user enable --now plasma-light-and-presence
```

## 6. 🧠 NPU and AI stack

```bash
sudo dnf install intel-npu-driver intel-npu-compiler
sudo dnf install openvino libopenvino-intel-npu-plugin python3-openvino-genai python3-openvino-tokenizers
sudo dnf install llama-cpp-vulkan llama-cpp-openvino
sudo dnf install onnxruntime-openvino python3-onnxruntime-openvino
sudo dnf install python3-optimum-intel python3-nncf python3-transformers
```

Useful tools from Fedora:

```bash
sudo dnf install intel-compute-runtime intel-level-zero oneapi-level-zero \
  intel-ocloc clinfo libva-utils igt-gpu-tools nvtop intel-lpmd
```

## 7. ✅ After the reboot

```bash
uname -r; mokutil --sb-state                       # ...dellptl..., SecureBoot enabled
sudo dmesg | grep -E "bind .* nlanes|All sensor registration"
sudo cat /sys/kernel/debug/dri/0000:00:02.0/eDP-1/vrr_range   # Min: 20 Max: 120
kscreen-doctor output.eDP-1.vrrpolicy.automatic
modinfo -n intel_ipu7                              # .../extra/intel-ipu7/...
ls -l /dev/ipu7-psys0
systemctl status thermald v4l2-relayd@ipu7 --no-pager | grep Active
```

The camera shows up as "Intel MIPI Camera" (`/dev/video50`).

If you installed the thermald drop-in or the signing hook by hand earlier, remove the `/etc` copies, they override the packaged ones:

```bash
sudo rm -f /etc/systemd/system/thermald.service.d/ptl-adaptive.conf \
  /etc/kernel/install.d/10-sign-dellptl.install
sudo systemctl daemon-reload
```

## 🧪 Trying the NPU

Run a model on the NPU, the GPU and the CPU with OpenVINO GenAI. Channel-wise INT4 models (`*-int4-cw-ov`) work best on the NPU.

```bash
pip install --user huggingface_hub
hf download OpenVINO/Phi-3.5-mini-instruct-int4-cw-ov --local-dir ~/models/Phi-3.5-mini-instruct-int4-cw-ov
python3 ~/Github/xps-fedora/tools/openvino/bench.py ~/models/Phi-3.5-mini-instruct-int4-cw-ov NPU GPU CPU
```

Convert your own model with optimum-intel, symmetric channel-wise INT4 for the NPU:

```bash
optimum-cli export openvino -m Qwen/Qwen2.5-0.5B-Instruct \
  --weight-format int4 --sym --group-size -1 --ratio 1.0 ~/models/qwen2.5-0.5b-int4-cw-ov
```

Measured with OpenVINO GenAI 2026.4, Phi-3.5-mini INT4-CW, 128 tokens:

| Device         | First token                                        | Speed    |
| -------------- | -------------------------------------------------- | -------- |
| GPU (Arc B390) | 59 ms                                              | 53 tok/s |
| NPU            | 0.9 s (20.7 s first compile, then ~1 s from cache) | 33 tok/s |
| CPU            | 3.4 s                                              | 36 tok/s |

Qwen2.5-0.5B INT4-CW: GPU 229 tok/s (first token 66 ms), NPU 124 tok/s (313 ms, 7.5 s first compile), CPU 151 tok/s.
