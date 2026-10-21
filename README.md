# quantization-ladder

Experiments 122 and 122b (GGUF quantization ladder on Qwen3-0.6B, ARC-Easy). Experiment arms in this repo. Each folder has its own README, code, raw results, chart and verdict.

- [`122-quantization-ladder`](122-quantization-ladder/) Experiment 122: GGUF quantization ladder for Qwen3-0.6B on ARC-Easy (constrained letter scoring) — **PROVEN under the preregistered constrained-scoring rule**
- [`122b-quant-ladder-logprob`](122b-quant-ladder-logprob/) Experiment 122b: quantization ladder with likelihood scoring and option rotation — **DISPROVEN**

Large artifacts excluded from git are attached to release [`v1-data`](https://github.com/nankris/quantization-ladder/releases/tag/v1-data); see [RELEASE_ASSETS.md](RELEASE_ASSETS.md).
