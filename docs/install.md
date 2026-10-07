# Installing

## 1. Secure Boot key (once)

Locally built kernels and kernel modules must be signed with a key that is
enrolled in shim's MOK list. The akmods key is used for both.

```bash
sudo dnf install akmods sbsigntools
sudo kmodgenca -a                       # /etc/pki/akmods/{certs,private}
sudo mokutil --import /etc/pki/akmods/certs/public_key.der
# reboot, then in MOK Manager: Enroll MOK, Continue, Yes, password, Reboot
mokutil --list-enrolled | grep Subject  # the obsidian-xps key is listed
```

## 2. Repositories

RPM Fusion free + nonfree (for `intel-media-driver`, `v4l2-relayd`,
`akmod-v4l2loopback`).

Remove RPM Fusion's IPU6 camera stack if it was installed. Its `libcamhal`
and `icamerasrc` conflict with the IPU7 ones:
```bash
sudo dnf remove akmod-intel-ipu6 'kmod-intel-ipu6*' ipu6-camera-hal \
  ipu6-camera-bins gstreamer1-plugins-icamerasrc
```

## 3. Packages

From `output/RPMS` (or the COPR repo once it exists). Install
`dell-xps-ptl-config` first, so its signing hook is in place when the kernel
installs:

```bash
cd output/RPMS
sudo dnf install noarch/dell-xps-ptl-config-*.rpm
sudo dnf install x86_64/kernel{,-core,-modules,-modules-core,-modules-extra,-devel}-7.2.9-300.dellptl.fc45.x86_64.rpm \
  x86_64/{akmod,kmod}-intel-ipu7-*.rpm x86_64/intel-ipu7-camera-*.rpm \
  x86_64/intel-npu-driver-1.38*.rpm x86_64/intel-npu-compiler-*.rpm
# build the IPU7 kmods for every installed kernel
sudo akmods --force --kernels 7.2.9-300.dellptl.fc45.x86_64
```

Useful Fedora / RPM Fusion extras:
```bash
sudo dnf install intel-compute-runtime intel-level-zero oneapi-level-zero \
  intel-ocloc clinfo libva-utils igt-gpu-tools nvtop intel-lpmd \
  intel-media-driver
```

If you installed the thermald drop-in or signing hook by hand earlier, remove
the `/etc` copies (they override the packaged ones):
```bash
sudo rm -f /etc/systemd/system/thermald.service.d/ptl-adaptive.conf \
  /etc/kernel/install.d/10-sign-dellptl.install
sudo systemctl daemon-reload
```

## 4. After reboot: verify

```bash
uname -r; mokutil --sb-state                       # ...dellptl..., enabled
sudo dmesg | grep -E "Panel Replay ALPM|bind .* nlanes|All sensor registration"
sudo cat /sys/kernel/debug/dri/0000:00:02.0/eDP-1/vrr_range   # Min: 20 Max: 120
kscreen-doctor output.eDP-1.vrrpolicy.automatic
modinfo -n intel_ipu7                              # .../extra/intel-ipu7/...
ls -l /dev/ipu7-psys0
systemctl status thermald v4l2-relayd@ipu7 --no-pager | grep Active
```
The camera shows up as "Intel MIPI Camera" (`/dev/video50`).

## OpenVINO / GenAI

Fedora's `openvino` (2026.0, split into `libopenvino-*` subpackages) has the
CPU and GPU plugins but is built without the NPU plugin and has no GenAI or
tokenizers, so use the PyPI wheels. Fedora's default Python is too new for them, so use 3.12:

```bash
mkdir -p ~/openvino-genai && cd ~/openvino-genai
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python openvino openvino-genai openvino-tokenizers huggingface_hub
.venv/bin/hf download OpenVINO/Phi-3.5-mini-instruct-int4-cw-ov \
  --local-dir models/Phi-3.5-mini-instruct-int4-cw-ov
.venv/bin/python ~/Github/xps-fedora/tools/openvino/bench.py models/Phi-3.5-mini-instruct-int4-cw-ov NPU GPU CPU
```
For the NPU, use channel-wise INT4 models (`*-int4-cw-ov`).

### Converting your own models (optimum-intel + nncf)

`optimum-intel` and `nncf` are PyPI-only (not in Fedora or Intel's YUM repo).
Use the CPU build of PyTorch, and take `torchvision` from the **same** index:
a mismatched torchvision breaks every `transformers` import with
`operator torchvision::nms does not exist`.

```bash
uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu torch torchvision
uv pip install --python .venv/bin/python "optimum-intel[openvino,nncf]"
# NPU-friendly: symmetric, channel-wise (group size -1) INT4
.venv/bin/optimum-cli export openvino -m Qwen/Qwen2.5-0.5B-Instruct \
  --weight-format int4 --sym --group-size -1 --ratio 1.0 models/qwen2.5-0.5b-int4-cw-ov
```

Qwen2.5-0.5B INT4-CW (converted here, ~2 min): GPU 229 tok/s (TTFT 66 ms),
NPU 124 tok/s (TTFT 313 ms, 7.5 s first compile), CPU 151 tok/s.

Measured (OpenVINO GenAI 2026.4, Phi-3.5-mini INT4-CW, 128 tokens, packaged
`intel-npu-driver` + `intel-npu-compiler` 1.38.0):

| Device | First token | Speed |
|---|---|---|
| GPU (Arc B390) | 59 ms | 53 tok/s |
| NPU | 0.9 s (20.7 s first compile, then ~1 s from cache) | 33 tok/s |
| CPU | 3.4 s | 36 tok/s |
