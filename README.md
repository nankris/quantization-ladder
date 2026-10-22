# quantization-ladder

GGUF quantization ladder on Qwen3-0.6B with ARC-Easy, in two independent studies. Each folder has its own README, code, raw results, charts and verdict.

- [`original-run`](original-run/): GGUF quantization ladder for Qwen3-0.6B on ARC-Easy (constrained letter scoring), **PROVEN under the preregistered constrained-scoring rule**
- [`quant-ladder-logprob`](quant-ladder-logprob/): the same ladder re-tested with likelihood scoring and option rotation on fresh questions, **DISPROVEN**
- [`issues-found`](issues-found/): issues raised by an independent review of both studies

Large artifacts excluded from git are attached to release [`v1-data`](https://github.com/nankris/quantization-ladder/releases/tag/v1-data); see [RELEASE_ASSETS.md](RELEASE_ASSETS.md).
