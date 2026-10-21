#!/usr/bin/env bash
set -euo pipefail
source /workspace/tools/setup.sh
sudo apt-get update
sudo apt-get install -y build-essential
/workspace/tools/mlenv/bin/pip install cmake ninja
CMAKE_ARGS='-DGGML_BLAS=OFF -DGGML_NATIVE=ON -DLLAMA_CURL=OFF' CMAKE_BUILD_PARALLEL_LEVEL=2 /workspace/tools/mlenv/bin/pip install llama-cpp-python==0.3.36
