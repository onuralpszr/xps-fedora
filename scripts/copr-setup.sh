#!/bin/bash
# Register every package as a COPR SCM package that builds straight from this
# GitHub repository (.copr/Makefile), with webhook rebuilds on. After this,
# a push that changes packages/<name>/ rebuilds only that package, once the
# COPR webhook is added to the GitHub repository (see docs/ci.md).
#
# Usage: scripts/copr-setup.sh            register or update all packages
# Safe to run again: existing packages are edited, not duplicated.
set -euo pipefail

repo=${REPO_URL:-https://github.com/onuralpszr/xps-fedora.git}
branch=${REPO_BRANCH:-main}
owner=${COPR_OWNER:-thunderbirdtr}

# package -> COPR project
declare -A project=(
  [onnx]=intel-ai-stack
  [openvino]=intel-ai-stack
  [openvino-genai]=intel-ai-stack
  [onnxruntime]=intel-ai-stack
  [llama-cpp]=intel-ai-stack
  [intel-npu-driver]=intel-ai-stack
  [python-openvino-telemetry]=intel-ai-stack
  [python-transformers]=intel-ai-stack
  [python-nncf]=intel-ai-stack
  [python-optimum]=intel-ai-stack
  [python-optimum-intel]=intel-ai-stack
  [dell-xps-ptl-config]=xps-fedora
  [intel-ipu7-kmod]=xps-fedora
)
# The kernel builds from Fedora dist-git (scripts/build-kernel.sh srpm) and
# intel-ipu7-camera contains closed libraries, so neither is registered here.

for pkg in "${!project[@]}"; do
  proj=$owner/${project[$pkg]}
  args=(--name "$pkg" --clone-url "$repo" --commit "$branch"
        --subdir "packages/$pkg" --spec "$pkg.spec"
        --method make_srpm --webhook-rebuild on)
  if copr-cli get-package "$proj" --name "$pkg" >/dev/null 2>&1; then
    copr-cli edit-package-scm "$proj" "${args[@]}" >/dev/null
    echo "updated    $proj $pkg"
  else
    copr-cli add-package-scm "$proj" "${args[@]}" >/dev/null
    echo "registered $proj $pkg"
  fi
done

# plasma-sensord lives in its own repository with its own .copr/Makefile; it
# has its own COPR and xps-fedora carries a copy for one-stop installs
for proj in "$owner/plasma-sensord" "$owner/xps-fedora"; do
  args=(--name plasma-sensord
        --clone-url "${SENSORD_URL:-https://github.com/onuralpszr/plasma-sensord.git}"
        --commit "$branch" --spec packaging/plasma-sensord.spec
        --method make_srpm --webhook-rebuild on)
  if copr-cli get-package "$proj" --name plasma-sensord >/dev/null 2>&1; then
    copr-cli edit-package-scm "$proj" "${args[@]}" >/dev/null
    echo "updated    $proj plasma-sensord"
  else
    copr-cli add-package-scm "$proj" "${args[@]}" >/dev/null
    echo "registered $proj plasma-sensord"
  fi
done
