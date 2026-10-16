# 📦 GPU and NPU in containers

Rootless Podman on Fedora 45 with SELinux enforcing, tested on 2026-10-12 on the Dell XPS 16 DA16260 (Arc B390 with `xe`, NPU 5010 with `intel_vpu`), podman 6.1.3. Docker (rootful) takes the same `--device` flags.

## 🏁 Summary

| Device | Node | Works rootless? | Needs |
| --- | --- | :---: | --- |
| 🎮 GPU (compute, Vulkan, VA-API) | `/dev/dri/renderD128` | ✅ | `--device /dev/dri/renderD128` |
| ⚡ NPU | `/dev/accel/accel0` | ✅ | `--device /dev/accel/accel0` and `--security-opt label=disable` |
| 📷 Camera (relay) | `/dev/video50` | ✅ | `--device /dev/video50` and `--user root` |

```bash
podman run --rm -it \
  --device /dev/dri/renderD128 \
  --device /dev/accel/accel0 \
  --security-opt label=disable \
  IMAGE
```

## 🔐 Why these flags

- **Permissions.** `renderD128` and `accel0` are mode `0666` (systemd's `50-udev-default.rules` sets `accel` nodes world writable), so rootless containers need no `--group-add`. Pass `renderD128` rather than all of `/dev/dri`: compute, Vulkan and VA-API only need the render node.
- **SELinux and the GPU.** `renderD128` is labelled `dri_device_t`, which the `container_use_dri_devices` boolean (on by default) allows. The GPU works with labels on.
- **SELinux and the NPU.** `accel0` has the generic `device_t` label, which containers may not open. With labels on, OpenVINO lists only `CPU` and `GPU` and `ls /dev/accel/accel0` inside the container says `Permission denied`. `--security-opt label=disable` fixes it for that container only. The `container_use_devices` boolean would allow it host wide, which is broader than needed.
- **Camera.** `/dev/video50` (the `v4l2-relayd` "Intel MIPI Camera") is `0660 root:video` with an ACL for the logged-in user. Rootless Podman maps that user to container root, so images that run as their own non-root user (DL Streamer runs as `dlstreamer`) lose access. `--user root` keeps it; container root is still just your user on the host. Use the relay node, not the raw IPU7 nodes, which are root only on purpose.

## 🧩 What the image must bring

The host gives only the kernel drivers and firmware. Inside the image:

- **GPU compute:** Intel compute-runtime and Level Zero, new enough for Xe3 (the host runs 26.35).
- **NPU:** the user space NPU driver (`libze_intel_npu`) and its compiler, from the same release line as the host (1.38 here).
- **Vulkan:** a recent Mesa ANV (llama.cpp Vulkan).
- **Media:** the iHD VA-API driver.

If an image is too old for Panther Lake, `GPU` disappears from OpenVINO's device list. A `fedora:45` image with this repository's COPRs matches the host exactly.

## ✅ Check a container

```bash
python3 -c "import openvino as ov; c = ov.Core(); print(c.available_devices)"   # ['CPU', 'GPU', 'NPU']
ls -l /dev/dri /dev/accel
```

## 🎥 Example: DL Streamer on the camera, GPU against NPU

[DL Streamer](https://github.com/open-edge-platform/dlstreamer) is Intel's GStreamer video analytics framework. It is not packaged as an RPM here: its `gvadetect` and related elements need GStreamer analytics APIs that Intel patches into its own GStreamer build and Fedora's 1.28 does not have. The official image runs as is:

```bash
mkdir -p ~/dls-models/face-detection-adas-0001/FP16 && cd "$_"
B=https://storage.openvinotoolkit.org/repositories/open_model_zoo/2023.0/models_bin/1/face-detection-adas-0001/FP16
curl -LO $B/face-detection-adas-0001.xml -LO $B/face-detection-adas-0001.bin

podman run --rm --user root --security-opt label=disable \
  --device /dev/dri/renderD128 --device /dev/accel/accel0 --device /dev/video50 \
  -v ~/dls-models:/models:ro docker.io/intel/dlstreamer:2026.2.0-ubuntu24 \
  gst-launch-1.0 v4l2src device=/dev/video50 num-buffers=300 ! videoconvert ! \
    gvadetect model=/models/face-detection-adas-0001/FP16/face-detection-adas-0001.xml device=NPU ! \
    gvafpscounter ! fakesink sync=false
```

| `device=` | Face detection on the camera | Load |
| --- | --- | --- |
| `GPU` | 13.7 fps | GPU about 15 % busy |
| `NPU` | 14.0 fps | NPU about 16 % busy, GPU idle |

Both are limited by the camera, which drops to about 15 fps in dim light, not by the detector. The NPU does the same work and leaves the GPU to the desktop, which makes it the better place for always-on video analytics.

## 📝 Notes

- Images tried or recommended: `docker.io/intel/dlstreamer:2026.2.0-ubuntu24` (tested), `openvino/ubuntu24_runtime`, `openvino/model_server:latest-gpu`, `ghcr.io/ggml-org/llama.cpp:server-vulkan`.
- DL Streamer 2026.2.0 was built against NPU driver 1.33; it ran fine on this host's 1.38 kernel side.
- If the NPU is missing, look for a denial on the host with `sudo ausearch -m avc -ts recent`.
