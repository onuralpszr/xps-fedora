# CI and automatic COPR builds

Two COPR projects build the packages in this repository:

| Project                                                                                                                     | Packages                                                                                         |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| [thunderbirdtr/intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/)                       | onnx, openvino, openvino-genai, onnxruntime, llama-cpp, whisper-cpp, intel-npu-driver and the Python packages |
| [thunderbirdtr/xps-fedora](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/)                               | dell-xps-ptl-config, intel-ipu7-kmod, kernel, plasma-light-and-presence                          |
| [thunderbirdtr/plasma-light-and-presence](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/plasma-light-and-presence/) | plasma-light-and-presence (from its own repository)                                              |

## How it fits together

- **On every pull request and push**, the [Check](../.github/workflows/check.yml) workflow parses the spec of each changed package, runs rpmlint and builds its source RPM, and runs shellcheck on the scripts.
- **On every push to main**, GitHub calls the COPR webhook. COPR rebuilds only the packages whose `packages/<name>/` directory changed. It builds the source RPM itself with [.copr/Makefile](../.copr/Makefile).
- **By hand**, the [COPR build](../.github/workflows/copr.yml) workflow in the Actions tab starts a build of any package, optionally for one chroot.
- **The kernel** builds from Fedora dist-git, so it is not part of the webhook. Build its source RPM with `scripts/build-kernel.sh srpm` and upload it with `copr-cli build thunderbirdtr/xps-fedora output/srpm/kernel/*.src.rpm`.
- **Every day**, the [Upstream watch](../.github/workflows/upstream-watch.yml) workflow looks for Fedora updates that would replace or break the COPR packages:
  - A new Fedora 45 kernel in Bodhi (testing or stable): it points [packages/kernel/fedora-base](../packages/kernel/fedora-base) at that kernel, checks that every patch in [packages/kernel/series](../packages/kernel/series) still applies, starts the COPR build and opens a pull request with the change. If a patch no longer applies, it opens an issue instead.
  - A newer Fedora or RPM Fusion build of a package rebuilt against our onnxruntime (calibre, crow-translate, gstreamer1-plugins-bad-free, monado, pipewire, vcmi): it rebuilds that package with `scripts/fedora-rebuild.sh` and starts a COPR build.
  - Run the same checks by hand with `scripts/upstream-watch.sh kernel` and `scripts/upstream-watch.sh rebuilds`.

## The kernel

The kernel spec is Fedora's own and is not kept here. Three files describe our kernel:

| File | What it holds |
| --- | --- |
| [fedora-base](../packages/kernel/fedora-base) | the Fedora dist-git commit and version it builds on, and our release on top (`local_release`, bump it when the patches change) |
| [series](../packages/kernel/series) | the patches to apply, in order |
| [kernel-local](../packages/kernel/kernel-local) | extra kernel config options |

`scripts/kernel-apply.sh` edits Fedora's spec by its anchors instead of applying a fixed diff, so the same files work on every new Fedora kernel as long as the patches apply.

## Turning it on

Do this once, after the repository is on GitHub.

1. Register the packages in COPR as SCM packages with webhook rebuilds:

   ```bash
   scripts/copr-setup.sh
   ```

2. Add the COPR webhooks to the GitHub repositories (xps-fedora and plasma-light-and-presence). For each project, open its COPR page, go to **Settings**, then **Integrations**, and copy the GitHub webhook URL. In the GitHub repository, open **Settings**, then **Webhooks**, then **Add webhook**: paste the URL, choose `application/json`, and keep **Just the push event**. Repeat for the second project.

3. Give the manual and daily workflows access to COPR. Create an API token at [copr.fedorainfracloud.org/api](https://copr.fedorainfracloud.org/api/) and store the whole configuration as a repository secret:

   ```bash
   gh secret set COPR_CONFIG < ~/.config/copr
   ```

4. Let the daily workflow open pull requests: in the GitHub repository, open **Settings**, then **Actions**, then **General**, and turn on **Allow GitHub Actions to create and approve pull requests**.

## Checking a change locally

```bash
make -f .copr/Makefile srpm spec=packages/<name>/<name>.spec outdir=/tmp/srpm
scripts/mock-build.sh <name>
```
