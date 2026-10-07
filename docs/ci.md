# CI and automatic COPR builds

Two COPR projects build the packages in this repository:

| Project | Packages |
|---|---|
| [thunderbirdtr/intel-ai-stack](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/intel-ai-stack/) | onnx, openvino, openvino-genai, onnxruntime, llama-cpp, intel-npu-driver and the Python packages |
| [thunderbirdtr/xps-fedora](https://copr.fedorainfracloud.org/coprs/thunderbirdtr/xps-fedora/) | dell-xps-ptl-config, intel-ipu7-kmod, kernel, plasma-sensord |

## How it fits together

* **On every pull request and push**, the [Check](../.github/workflows/check.yml) workflow parses the spec of each changed package, runs rpmlint and builds its source RPM, and runs shellcheck on the scripts.
* **On every push to main**, GitHub calls the COPR webhook. COPR rebuilds only the packages whose `packages/<name>/` directory changed. It builds the source RPM itself with [.copr/Makefile](../.copr/Makefile).
* **By hand**, the [COPR build](../.github/workflows/copr.yml) workflow in the Actions tab starts a build of any package, optionally for one chroot.
* **The kernel** builds from Fedora dist-git, so it is not part of the webhook. Build its source RPM with `scripts/build-kernel.sh srpm` and upload it with `copr-cli build thunderbirdtr/xps-fedora output/srpm/kernel/*.src.rpm`.

## Turning it on

Do this once, after the repository is on GitHub.

1. Register the packages in COPR as SCM packages with webhook rebuilds:

   ```bash
   scripts/copr-setup.sh
   ```

2. Add the COPR webhooks to the GitHub repository. For each project, open its COPR page, go to **Settings**, then **Integrations**, and copy the GitHub webhook URL. In the GitHub repository, open **Settings**, then **Webhooks**, then **Add webhook**: paste the URL, choose `application/json`, and keep **Just the push event**. Repeat for the second project.

3. Give the manual workflow access to COPR. Create an API token at [copr.fedorainfracloud.org/api](https://copr.fedorainfracloud.org/api/) and store the whole configuration as a repository secret:

   ```bash
   gh secret set COPR_CONFIG < ~/.config/copr
   ```

## Checking a change locally

```bash
make -f .copr/Makefile srpm spec=packages/<name>/<name>.spec outdir=/tmp/srpm
scripts/mock-build.sh <name>
```
