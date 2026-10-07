# Fedora downstream to-do

The work needed to move the packages in this repository from COPR into Fedora. Details, reverse dependencies and PR texts are in [downstream.md](downstream.md).

✅ done, ⏳ in progress or waiting, ⚠️ needs a decision or a fix, ⛔ blocked

## 1. Ready in COPR

- [x] ✅ onnx 1.22.0 builds on f45 and rawhide
- [x] ✅ openvino 2026.4.1 with the NPU plugin builds on f45 and rawhide
- [x] ✅ onnxruntime 1.30.0 builds on f45 and rawhide
- [x] ✅ openvino-genai 2026.4.1.0 and openvino-tokenizers build on f45 and rawhide
- [x] ✅ intel-npu-driver 1.38.0 builds on f45 and rawhide
- [x] ✅ calibre, crow-translate, gstreamer1-plugins-bad-free and pipewire rebuilt against onnxruntime 1.30
- [ ] ⏳ llama-cpp b11460 (f45 and rawhide)
- [ ] ⏳ monado and vcmi rebuilds
- [ ] ⏳ python-torch rebuild on rawhide, then python-optimum-intel on rawhide
- [ ] ⚠️ Add ollama to the COPR rebuilds (it links `libggml-base.so.0`)
- [ ] ⚠️ Add `Recommends` for the llama-cpp backend subpackages so a plain install keeps GPU support

## 2. Prepare the dist-git changes

- [ ] Switch every spec back to `%autorelease` and `%autochangelog`, keeping the commit message as the changelog entry
- [ ] Rebase onnx on dist-git PR #17 ("Remove protobuf-devel buildreq") once it is merged
- [ ] Rebase llama-cpp on the rawhide spec (b11232) for the rawhide PR
- [ ] ⚠️ Split `intel-npu-compiler` out of `intel-npu-driver`: Fedora will not take the prebuilt compiler, it needs its own review and a from-source build
- [ ] Run a Koji scratch build of each package on rawhide before opening the PR

## 3. Talk to the maintainers first

- [ ] openvino: comment on dist-git PR #10 (Intel, same NPU work) and offer to join it instead of opening a competing PR
- [ ] onnx and onnxruntime: agree on the bump with the maintainer (dherrera) and wait for FEDORA-2026-de31921a47 (onnxruntime 1.26.0-13) to leave testing on f45
- [ ] intel-npu-driver: coordinate 1.38 with the maintainer (androniychuk), the f45 1.35 build is still pending
- [ ] llama-cpp and ollama: ask the maintainers about the backend subpackages and the ollama rebuild
- [ ] Tell the maintainers of calibre, crow-translate, gstreamer1-plugins-bad-free, monado, pipewire and python-torch about the rebuilds, or ask a provenpackager

## 4. intel-npu-driver on its own

- [ ] Open the rawhide PR for intel-npu-driver 1.38.0 (closes bug 2391451)
- [ ] Build in rawhide, then f45, and file the Bodhi update

## 5. Rawhide side tag

- [ ] `fedpkg request-side-tag` on rawhide
- [ ] onnx 1.22.0
- [ ] openvino 2026.4.1 (after `koji wait-repo` for onnx)
- [ ] onnxruntime 1.30.0 (closes bug 2350854)
- [ ] Rebuild calibre, crow-translate, gstreamer1-plugins-bad-free, monado and pipewire
- [ ] ⚠️ python-torch: scratch build against onnx 1.22 first, then rebuild in the side tag
- [ ] llama-cpp b11460
- [ ] Merge the side tag

## 6. Fedora 45 side tag

- [ ] `fedpkg request-side-tag` on f45
- [ ] onnx, openvino, onnxruntime in that order
- [ ] Rebuild calibre, crow-translate, gstreamer1-plugins-bad-free, monado and pipewire
- [ ] llama-cpp b11460 and an ollama rebuild
- [ ] One Bodhi update for the whole side tag, to updates-testing
- [ ] ⛔ Stable push after the Fedora 45 release, or with a freeze exception

## 7. RPM Fusion

- [ ] Ask RPM Fusion to rebuild vcmi on f45 and rawhide once onnxruntime 1.30 reaches testing

## 8. New packages for Fedora

Review requests, in this order:

- [ ] python-openvino-telemetry
- [ ] python-transformers
- [ ] python-optimum
- [ ] python-nncf
- [ ] openvino-genai (after openvino 2026.4.1 is in Fedora; unbundle sentencepiece, pcre2, nlohmann json and pybind11 where possible)
- [ ] python-optimum-intel

## 9. After the updates land

- [ ] Remove the matching packages from the COPR so Fedora's builds take over
- [ ] Keep the COPR for the packages Fedora does not ship (kernel, camera drivers, configuration)
