#!/usr/bin/env bash
set -euo pipefail
source /workspace/tools/setup.sh
cd "$(dirname "$0")/.."
for fmt in BF16 Q8_0 Q4_K_M Q3_K_M Q2_K; do
 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 /workspace/tools/mlenv/bin/python scripts/evaluate.py "$fmt" "$@" >> "results/run_${fmt}.log" 2>&1
done
