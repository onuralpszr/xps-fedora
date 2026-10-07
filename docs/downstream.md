# Fedora downstream plan

The step by step checklist is in [fedora-todo.md](fedora-todo.md).

This is the plan for sending the AI stack updates in `packages/` to Fedora. All data below comes from read-only queries on 2026-10-07: `dnf repoquery` against f45 (`fedora`, `updates`, `updates-testing`), rawhide (f46) and their source repos, RPM Fusion f45 binary and source repos, the src.fedoraproject.org API and raw spec files, Koji, Bodhi, Bugzilla and release-monitoring.org. Anything that could not be checked says so.

Facts that apply to every PR:

- F45 is **frozen** in Bodhi (state `frozen`). Updates can go to `updates-testing`, but a stable push before GA needs a freeze exception.
- Every Fedora spec here uses `%autorelease` and `%autochangelog`. Our specs use `Release: 1%{?dist}` and a written changelog. Each PR has to switch back to `%autorelease` / `%autochangelog`, drop our changelog entry, and use the commit message as the changelog.
- The f45 and rawhide dist-git specs of onnx, onnxruntime, openvino and intel-npu-driver are the same file. llama-cpp differs (rawhide is at b11232 and builds the `lib*-impl` tool libraries as static); our llama-cpp spec is based on f45 b9840, so the rawhide PR has to be rebased on the rawhide spec.
- The last onnx/onnxruntime bump used side tag `f45-build-side-142200`, Bodhi update FEDORA-2026-916652ebea (dherrera): onnx, onnxruntime, calibre, crow-translate, gstreamer1-plugins-bad-free, monado, pipewire. That is the model for this round.
- COPR `thunderbirdtr/intel-ai-stack` state at the time of writing: onnx, openvino, intel-npu-driver, python-openvino-telemetry, python-transformers, python-optimum and python-nncf (3.4.0-2) succeeded on f45 and rawhide; onnxruntime, llama-cpp and openvino-genai were running; the ORT dependent rebuilds and python-optimum-intel were pending.

## onnx 1.21.0 to 1.22.0

### Current Fedora state

|             | f45                                        | rawhide                                       |
| ----------- | ------------------------------------------ | --------------------------------------------- |
| Build       | onnx-1.21.0-5.fc45                         | onnx-1.21.0-5.fc45 (inherited, no fc46 build) |
| Subpackages | onnx-libs, onnx-devel, python3-onnx        | same                                          |
| Sonames     | libonnx.so.1.21.0, libonnx_proto.so.1.21.0 | same                                          |

- Maintainers: owner dherrera; collaborators pbrobinson, withenoughcoffee.
- Open PRs: #17 (rawhide, carlwgeorge, 2026-09-23) "Remove protobuf-devel buildreq", approved in a comment by pbrobinson, not merged. Our spec still has `BuildRequires: protobuf-devel`; rebase on top of #17 once it lands.
- Fedora carries 7 patches (0001 to 0007); ours replaces them with 2 (`0001-Fedora-shared-libraries.patch`, `0002-Add-fixes-for-use-with-onnxruntime.patch`) because 1.22 moved to scikit-build-core and hides symbols.
- Open bugs: 2365773 "onnx-1.23.2 is available" (release monitoring). 1.22.0 does **not** close it; upstream is at 1.23.2, but OpenVINO 2026.4 and onnxruntime 1.30 pin 1.22. CVE trackers 2454175, 2454676, 2454893 (CVE-2026-27489, -34446, -34445) describe issues fixed in 1.21.0, which Fedora already ships. 2448797 (CVE-2026-28500) had no upstream fix at publication; could not check whether 1.22.0 fixes it.

### Reverse dependencies

| Package | Why it depends | f45 | rawhide | Impact | Action |
| --- | --- | --- | --- | --- | --- |
| openvino (`libopenvino-onnx-frontend`) | links libonnx.so.1.21.0 and libonnx_proto.so.1.21.0; BR onnx-devel | yes | yes | soname change, uninstallable until rebuilt | updated in the same side tag (our openvino needs onnx-devel >= 1.22) |
| onnxruntime (all variants: base, migraphx, openvino, tests, python3) | links libonnx.so.1.21.0; BR onnx-devel | yes | yes | soname change | updated in the same side tag (our spec needs onnx-devel = 1.22.0) |
| python-torch (`python3-torch`) | links libonnx.so.1.21.0 and libonnx_proto.so.1.21.0; BR onnx-devel (`%bcond_without onnx`, `USE_SYSTEM_ONNX=ON`) | no (2.12.0-7.fc45 bundles onnx 1.18.0) | **yes** (2.13.0-4.fc46) | soname change; torch builds C++ code against the onnx API, so 1.22 may need source fixes | rebuild in the rawhide side tag; needs a scratch build first; owner trix |
| python-piper-tts | BR python3dist(onnx) only | yes | yes | build only, no version pin | none |

No RPM Fusion package depends on onnx (checked f45 binary and source repos).

### PR

- Title: `Update to 1.22.0.`
- Description: `Update to onnx 1.22.0, which onnxruntime 1.30 and OpenVINO 2026.4 build against, and port the shared library patches to the new scikit-build-core build.`

## openvino 2026.0.0 to 2026.4.1

### Current Fedora state

|            | f45                                                                                                     | rawhide                   |
| ---------- | ------------------------------------------------------------------------------------------------------- | ------------------------- |
| Build      | openvino-2026.0.0-16.fc45 (stable, FEDORA-2026-61974f9b70)                                              | openvino-2026.0.0-17.fc46 |
| Sonames    | libopenvino.so.2600, libopenvino_c.so.2600, libopenvino_onnx_frontend.so.2600 (and the other frontends) | same                      |
| NPU plugin | `-DENABLE_INTEL_NPU=OFF`                                                                                | same                      |

- Maintainers: owner aanokhov; admins ajax, androniychuk; commit xanderlent.
- Open PRs: **#10** (rawhide, aaroncyew, Intel, opened 2026-06-15, last update 2026-10-06, 51 comments) "Add NPU Plugin/Compiler support to Openvino 2026.0.0". It overlaps with our NPU work. In that thread ajax says the compiler (`npucompiler.spec`) should go through a new package review as `intel-npu-compiler`, and nielsdg notes the NPU plugin still does not show up. Our PR should be coordinated with #10 (build on it or ask to supersede it) rather than opened blind.
- Patches: Fedora has protobuf_version, xbyak-gflags-system-modules, samples-system-gflags-json, pybind11-call_guard-compat(-3x), opencl-clhpp-deprecated-macro. Ours drops the pybind11 and OpenCL-CLHPP patches (upstream) and adds `npu-system-level-zero.patch` plus the level-zero-npu-extensions source.
- Open bugs: no release-monitoring bug is open. 2488271 (F44) "Intel NPU compile fails via Fedora driver compiler" is related to the NPU work but is filed against F44 and is not fixed by this PR alone. The node-tar CVE trackers (2431089, 2431115, 2434839, 2441361, 2498660, 2498753, 2498765, 2498782, 2498799) are against bundled JavaScript; could not check whether 2026.4.1 still ships the affected code.

### Reverse dependencies

| Package                                                                       | Why it depends                                                                                | f45                                                                              | rawhide | Impact                 | Action                                                                |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------- | ---------------------- | --------------------------------------------------------------------- |
| onnxruntime-openvino, python3-onnxruntime-openvino, onnxruntime-openvino-test | link libopenvino.so.2600; BR openvino-devel                                                   | f45 only in updates-testing (onnxruntime-1.26.0-13.fc45, FEDORA-2026-de31921a47) | yes     | soname change to .2641 | updated in the same side tag (our ORT needs openvino-devel >= 2026.4) |
| llama-cpp-openvino (new subpackage)                                           | BR openvino-devel                                                                             | new                                                                              | new     | new user               | build after openvino in the same side tag                             |
| whisper-cpp                                                                   | `%bcond_with openvino` (disabled, comment "FTBFS 7/27/26 openvino needs rebuilding at least") | no                                                                               | no      | none today             | none; the maintainer may want to try re-enabling it after the update  |
| openvino-genai (new package)                                                  | BR openvino-devel                                                                             | new                                                                              | new     | new user               | review after openvino 2026.4.1 is in Fedora                           |

No package requires python3-openvino, python3dist(openvino), cmake(OpenVINO) or pkgconfig(openvino) in f45 or rawhide. No RPM Fusion package depends on openvino (checked f45 binary and source repos).

Other notes:

- The NPU plugin `Recommends: intel-npu-compiler`, which only exists in our intel-npu-driver spec (prebuilt). Without it Fedora gets the plugin but it cannot compile models. See intel-npu-driver below.
- Plugins live in `%{_libdir}/openvino-%{version}`, so the directory name changes with the version; all plugin subpackages are rebuilt together, so this is fine.

### PR

- Title: `Update to 2026.4.1 and enable the Intel NPU plugin.`
- Description: `Update to 2026.4.1, build against onnx 1.22, enable the NPU plugin against the system Level Zero, add the GGUF frontend subpackage and drop the pybind11 and OpenCL-CLHPP patches that are now upstream.`

## onnxruntime 1.26.0 to 1.30.0

### Current Fedora state

|                | f45                                                                                                  | rawhide                    |
| -------------- | ---------------------------------------------------------------------------------------------------- | -------------------------- |
| Stable         | onnxruntime-1.26.0-9.fc45                                                                            | onnxruntime-1.26.0-13.fc46 |
| Testing        | onnxruntime-1.26.0-13.fc45 (FEDORA-2026-de31921a47, submitted 2026-10-06, adds the openvino variant) | n/a                        |
| Symbol version | libonnxruntime.so.1(VERS_1.26.0)                                                                     | same                       |

- Maintainers: owner dherrera; commit carlwgeorge.
- Open PRs: none.
- Our patches 0001 to 0011 keep Fedora's names (0001 and 0002 rebased); 0012-System-cpuinfo.patch is new because 1.30 always fetches its own cpuinfo. Our spec is based on the -13 spec (has the openvino bcond).
- Open bugs this update closes: **2350854** "onnxruntime-1.30.0 is available". 2383230 and 2385363 (FTBFS) are ON_QA through FEDORA-2026-de31921a47, not through ours. The many CVE trackers (node-tar, lodash, protobufjs, xmldom, ws, React Native CLI) are against bundled JavaScript; could not check whether 1.30.0 still ships it.
- FEDORA-2026-de31921a47 is still in testing. Our update obsoletes it; wait for it or coordinate with dherrera so the two do not race.

### Reverse dependencies

All of these require `libonnxruntime.so.1(VERS_1.26.0)` unless noted, so every one becomes uninstallable until rebuilt. ORT's C API is versioned and kept backward compatible upstream, so a plain rebuild is expected to be enough; COPR rebuilds were still pending at the time of writing.

| Package | Why it depends | f45 | rawhide | Impact | Action |
| --- | --- | --- | --- | --- | --- |
| calibre | links libonnxruntime; BR onnxruntime-devel | 9.15.0-1.fc45 | 9.15.0-1.fc46 | symbol version | rebuild in side tag (owner kevin) |
| crow-translate | links libonnxruntime; BR pkgconfig(libonnxruntime) (`%bcond onnxruntime 1`) | 4.1.0-1.fc45 | same, fc46 | symbol version | rebuild (owner atim, kde-sig) |
| gstreamer1-plugins-bad-free (`-extras`, libgstonnx.so) | links libonnxruntime; BR pkgconfig(libonnxruntime) >= 1.16.1 | 1.28.7-2.fc45 | 1.28.7-3.fc46 | symbol version | rebuild (owner yselkowitz, multimedia-sig) |
| monado | links libonnxruntime; BR pkgconfig(libonnxruntime) on x86_64/aarch64 | 25.1.0^20260820git01c1f6b-2.fc45 | same, fc46 | symbol version | rebuild (owner jsteffan, xr-sig) |
| pipewire (`module-filter-chain-onnx`) | links libonnxruntime; BR onnxruntime-devel | 1.6.9-1.fc45 | 1.6.9-1.fc46 | symbol version | rebuild (owner wtaymans) |
| python-piper-tts (`python3-piper-tts`) | Requires python3-onnxruntime; BR python3dist(onnxruntime), range `>= 1, < 2` | 1.4.2-5.fc45 | same | Python only, range allows 1.30 | none |
| envision (`envision-monado`) | Requires onnxruntime-devel / pkgconfig(libonnxruntime) at runtime (builds Monado for the user) | 3.2.0^20260822git733995a-2.fc45 | same, fc46 | no soname link | none |
| darktable | BR onnxruntime-devel >= 1.18, `-DUSE_AI=ON`; no RPM runtime dependency on onnxruntime | 5.6.1-3.fc45 | 5.6.1-3.fc46 | could not check how it loads ORT (no link dependency shows up) | no rebuild required by RPM; ask the maintainer (germano) or include a rebuild to be safe |
| vcmi (RPM Fusion free) | links libonnxruntime (VERS_1.26.0); BR onnxruntime-devel | 1.7.5-2.fc45 (repo), spec at 1.7.5-3 | could not check (no RPM Fusion rawhide repo configured) | symbol version | rebuild in RPM Fusion right after the Fedora update; recent commits by Leigh Scott; owner could not check (pkgs.rpmfusion.org API returned 404) |

No dependency in these specs pins an exact onnxruntime version.

### PR

- Title: `Update to 1.30.0.`
- Description: `Update to onnxruntime 1.30.0, rebase patches 0001 and 0002, add a patch to use the system cpuinfo, and build against onnx 1.22.0 and OpenVINO 2026.4.1.`

Rebuild commits for the dependents (one per package, matching the commit style used for 1.26):

- Title: `Rebuild for libonnxruntime.so.1(VERS_1.30.0).`
- Description: `Rebuild against onnxruntime 1.30.0 in the side tag.`

## llama-cpp b9840 to b11460

### Current Fedora state

|             | f45                                                                           | rawhide                 |
| ----------- | ----------------------------------------------------------------------------- | ----------------------- |
| Build       | llama-cpp-b9840-2.fc45                                                        | llama-cpp-b11232-1.fc46 |
| Subpackages | llama-cpp, llama-cpp-devel                                                    | same                    |
| Backends    | HIP built into the main package (libggml-hip.so.0 in `%{_libdir}`), no Vulkan | same                    |

- Maintainers: owner trix; admin man2dev, rocm-packagers-sig.
- Open PRs: #14 (rawhide, jcajka, 2025-01-31) "Set proper exclude arch"; trix asked for maintainers with hardware for other arches. Not related.
- Open bugs: 2343019 "llama-cpp-0.6.0 is available" (release-monitoring maps the project to a wrong version scheme; this update does not close it). 2447309 "pkgconfig file should be in /usr/lib64/pkgconfig": our spec ships `%{_libdir}/pkgconfig/llama.pc`, so it may close it; could not check the reporter's exact case. CVE trackers 2448112, 2450676, 2453936 describe issues fixed in b8146, b7824 and b8492, older than what Fedora ships. The others (2448111, 2507585, 2514021, 2514596, 2514602, 2514728, 2514854 and the React Router ones) could not be matched to a fixed build number.

### Reverse dependencies

| Package | Why it depends | f45 | rawhide | Impact | Action |
| --- | --- | --- | --- | --- | --- |
| ollama | Requires llama-cpp; rawhide also BR llama-cpp-devel and runs the system `llama-server` | 0.24.0-4.fc45; `ollama-rocm` and `ollama-vulkan` link libggml-base.so.0 | 0.33.1-1.fc46, no library link | f45: ggml has no stable ABI and libggml-base.so.0 jumps from b9840 to b11460 under the same soname. Both: GPU backends move to `-hip` / `-vulkan` subpackages, so a plain `llama-cpp` install loses HIP | f45: rebuild ollama in the same update or confirm the ABI; both: add weak dependencies so ROCm users keep `llama-cpp-hip` (owner trix) |
| lemonade-server | Requires llama-cpp | 11.5.2-1.fc45 | 11.9.0-1.fc46 | same backend split; it uses the llama.cpp tools, no library link | none needed for RPM; ask kmarinos / rocm-packagers-sig whether it should require `llama-cpp-hip` or `-vulkan` |
| whisper-cpp | not a reverse dependency: ships its own `%{_libdir}/libggml*.so.0` | 1.8.3-4.fc45 | 1.9.3-2.fc46 | already owns the same libggml.so.0 / libggml-base.so.0 / libggml-cpu.so.0 / libggml-hip.so.0 symlinks as llama-cpp with different targets (existing file conflict). Our move of libggml-cpu and libggml-hip to `%{_libdir}/ggml` removes two of the four overlaps | none for this PR; worth a separate bug |

Nothing requires libggml-cpu.so.0 or libggml-hip.so.0 from llama-cpp, so dropping those sonames from `%{_libdir}` breaks no package. No RPM Fusion package depends on llama-cpp or ggml (checked f45 binary and source repos).

### PR

- Title: `Update to b11460 and build the ggml backends as loadable modules.`
- Description: `Update to b11460, build ggml with GGML_BACKEND_DL and all CPU variants, move the backends to %{_libdir}/ggml and add -vulkan, -openvino and -hip subpackages.`

## intel-npu-driver 1.35.0 to 1.38.0

### Current Fedora state

|               | f45                                     | rawhide                        |
| ------------- | --------------------------------------- | ------------------------------ |
| Build         | intel-npu-driver-1.32.0-2.fc45          | intel-npu-driver-1.35.0-1.fc46 |
| dist-git spec | 1.35.0 (merged but never built for f45) | 1.35.0                         |

- Maintainers: owner aekoroglu; admin androniychuk.
- In openvino PR #10 androniychuk wrote that the 1.35 update would be built for stable together with level-zero, after a spirv-headers update lands. f45 already has oneapi-level-zero 1.33.1.
- Open PRs: #16 (rawhide, aaroncyew, 2026-09-15) "Enable Fedora-ELN build", waiting on review.
- Open bugs this update closes: **2391451** "intel-npu-driver-1.38.0 is available". 2487433 (F44, bump request) is about F44, so it is only addressed if F44 is updated too. CVE trackers 2520372, 2520375, 2520377, 2520379 (rawhide) and 2477887 (CVE-2026-20718): could not check the fixed driver version from Bugzilla.
- Earlier review: 2360470 "Review Request: intel-npu-compiler" was closed NOTABUG in 2025-06 because the plan then was to build the compiler from the openvino package. In PR #10 (2026) ajax asks for a new `intel-npu-compiler` review instead.

### Reverse dependencies

| Package                            | Why it depends                                       | f45 | rawhide | Impact               | Action |
| ---------------------------------- | ---------------------------------------------------- | --- | ------- | -------------------- | ------ |
| libopenvino-intel-npu-plugin (new) | `Recommends: intel-npu-driver`, `intel-npu-compiler` | new | new     | weak dependency only | none   |

Nothing requires intel-npu-driver or libze_intel_npu.so.1 in Fedora or RPM Fusion apart from its own `-test` subpackage.

### The compiler subpackage

Our spec adds `intel-npu-compiler` built from Intel's prebuilt `linux-npu-driver-v1.38.0.*-ubuntu2604.tar.gz` (Apache-2.0). Fedora requires packages to be built from source, so this subpackage will most likely not be accepted. Proposal: send the driver update without it, and handle the compiler as its own review (`intel-npu-compiler`, built from openvinotoolkit/npu_compiler), as ajax asked in openvino PR #10. Until then the Fedora NPU plugin can load models but not compile them.

### PR

- Title: `Update to 1.38.0.`
- Description: `Update to 1.38.0 and replace the DDI initializer patch with one for 1.38 and oneapi-level-zero 1.33; the prebuilt NPU compiler is left out and will go through its own review.`

## Submission order

A side tag is needed: onnx changes soname, openvino changes soname and onnxruntime changes its symbol version, and each one is a build dependency of the next. Request one side tag per branch with `fedpkg request-side-tag` (rawhide first, then f45) and ship everything in it as one Bodhi update, as was done with `f45-build-side-142200`.

| Step | Package                                                                | Branch                     | Needs                             | Notes                                                                                                                                      |
| ---- | ---------------------------------------------------------------------- | -------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 0    | intel-npu-driver 1.38.0                                                | rawhide, f45               | nothing                           | separate normal update, no reverse dependencies; the f45 1.35 build is still pending with the maintainers, so coordinate with androniychuk |
| 1    | onnx 1.22.0                                                            | side tag                   | nothing                           | rebase on PR #17                                                                                                                           |
| 2    | openvino 2026.4.1                                                      | side tag                   | onnx 1.22                         | coordinate with PR #10 first                                                                                                               |
| 3    | onnxruntime 1.30.0                                                     | side tag                   | onnx 1.22, openvino 2026.4        | wait for FEDORA-2026-de31921a47 on f45                                                                                                     |
| 4    | calibre, crow-translate, gstreamer1-plugins-bad-free, monado, pipewire | side tag                   | onnxruntime 1.30                  | rebuild only; darktable optional                                                                                                           |
| 4    | python-torch                                                           | rawhide side tag only      | onnx 1.22                         | needs a scratch build first                                                                                                                |
| 5    | llama-cpp b11460                                                       | side tag                   | openvino 2026.4 (for `-openvino`) | could go later in its own update, but building it here avoids a second openvino dependency round                                           |
| 5    | ollama                                                                 | f45 side tag               | llama-cpp b11460                  | rebuild for the ggml ABI                                                                                                                   |
| 6    | Bodhi update from the side tag                                         | f45                        | all of the above                  | goes to updates-testing; stable after F45 GA or with a freeze exception                                                                    |
| 7    | vcmi                                                                   | RPM Fusion f45 and rawhide | onnxruntime 1.30 in Fedora        | ask RPM Fusion for a rebuild when the Fedora update reaches testing                                                                        |

Use `koji wait-repo <sidetag> --build <nvr>` between steps 1, 2, 3 and 5. Rebuilds of packages we do not maintain need the maintainers' agreement or a provenpackager; open the dist-git PRs early so they have time to answer.

## New packages

None of these exist in Fedora dist-git (src.fedoraproject.org returns 404) and no Package Review bug exists for any of them (Bugzilla component "Package Review", searched by name; the only hits were unrelated packages).

| Package | Version | Review status | Needs in Fedora first | Notes |
| --- | --- | --- | --- | --- |
| python-openvino-telemetry | 2025.2.0 | no review request | nothing | sends opt-in usage statistics; the reviewer will check that nothing is sent by default (Fedora telemetry rules) |
| python-transformers | 5.5.4 | no review request | Fedora's python-tokenizers, python-huggingface-hub, python-safetensors (reviews 2388154, 2292665, 2349303 closed as done) | pinned below 5.6 for optimum-intel 2.2; we relax the tokenizers cap to `< 0.24` |
| python-optimum | 2.3.0 | no review request | python-transformers | owns `optimum-cli` and the `optimum` namespace |
| python-nncf | 3.4.0 | no review request | python-openvino-telemetry | we relax the numpy cap |
| openvino-genai | 2026.4.1.0 | no review request | openvino 2026.4.1 | also builds openvino-tokenizers and python3-openvino-tokenizers; bundles sentencepiece, pcre2, nlohmann json, minja, safetensors.h, gguf-tools, xgrammar, dlpack and pybind11 from CMake FetchContent, which the review will question (sentencepiece, pcre2, json and pybind11 are already in Fedora) |
| python-optimum-intel | 2.2.0 | no review request | python-optimum, python-nncf, openvino-genai (openvino-tokenizers) | we relax the huggingface-hub cap |
| intel-npu-compiler | n/a | 2360470 closed NOTABUG (2025-06) | openvino | ajax asked for a new review in openvino PR #10; needs a from-source build |

Suggested review order: python-openvino-telemetry and python-transformers, then python-optimum and python-nncf, then openvino-genai once openvino 2026.4.1 is in Fedora, then python-optimum-intel.
