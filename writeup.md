# Quantization: five formats, one model

**4-bit kept 126.7% of the accuracy at 33.1% of the size.**

Overall preregistered verdict: **PROVEN**. Q4 accuracy: PROVEN; Q4 size: passes; Q2 degradation: PROVEN.

| Format | Correct /150 | Accuracy % | Δ vs BF16, pp (95% paired CI) | File MB | Size % | Peak host RSS MiB | Peak GPU MiB | Prompt tok/s | Generation tok/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BF16 | 60 | 40.00 | +0.00 [+0.00, +0.00] | 1198.18 | 100.00 | 1506.9 | 1566.0 | 12462.18 | 162.61 |
| Q8_0 | 64 | 42.67 | +2.67 [+0.67, +5.33] | 639.45 | 53.37 | 974.1 | 1040.0 | 11224.74 | 243.50 |
| Q4_K_M | 76 | 50.67 | +10.67 [+6.00, +16.00] | 396.71 | 33.11 | 744.0 | 810.0 | 11413.23 | 299.29 |
| Q3_K_M | 64 | 42.67 | +2.67 [-4.00, +9.33] | 347.13 | 28.97 | 750.2 | 762.0 | 11423.49 | 282.47 |
| Q2_K | 38 | 25.33 | -14.67 [-21.33, -8.00] | 296.24 | 24.72 | 745.0 | 714.0 | 10087.76 | 319.58 |

Q4 accuracy retention 95% paired bootstrap CI: [114.1%, 144.2%]. Retention is the ratio of observed test accuracies, not a fraction of capabilities preserved.

## Plain-English takeaway
On these 150 science questions, the 4-bit model answered 76 correctly versus 60 for the 16-bit model, using 33.1% as much disk space. BF16 strongly favored letter A, so the apparent accuracy gain is specific to this constrained test and does not establish that 4-bit is generally smarter.

## Measurement details and limits
Public ARC-Easy test sample, four-choice filter, NumPy seed 122; identical zero-shot non-thinking chat prompts for all formats. The selected answer has the largest raw next-token logit among the single-token letters A/B/C/D. BF16 is the available 16-bit baseline, rather than F16. Each item begins with a reset KV cache; all prompts and four logits are saved. No model tuning or prompt selection used measured accuracy.

llama-cpp-python 0.3.36 CUDA 12.4 wheel; NVIDIA L4, all model layers offloaded, two CPU threads, context 1024, batch 512, microbatch 128, 99 requested GPU layers (full offload), flash attention off, mmap on. Peak RSS is the fresh evaluator process high-water mark through evaluation and benchmarking, including file-backed model pages and Python/runtime overhead. GPU memory is the peak process allocation sampled through NVML every 50 ms, including the CUDA context; brief peaks may be missed. Native logits are fetched before stopping each timer to synchronize GPU work. Throughput is the median of three warm measurements after one warmup: 256 prompt tokens and 64 greedy generation evaluations, counting each token evaluation, ignoring EOS. It excludes tokenization and loading. These are descriptive timing measurements without inferential CIs; generation benchmark uses a common synthetic science prompt, not accuracy answers.

Accuracy differences and retention CIs use 20,000 paired item bootstrap resamples, seed 122, percentile 95% intervals. No multiple-comparison correction; hypotheses concern Q4 and Q2, other formats are descriptive. Sampling uncertainty does not capture prompt sensitivity, training-data contamination, dataset choice, or systematic model biases. Quantized GGUFs include higher-precision tensors, so format names do not imply all weights have that bit width. Their metadata records Unsloth importance-matrix calibration (688 chunks); this experiment compares those prebuilt artifacts and cannot isolate nominal bit width from the quantizer/calibration recipe.

BF16 predicted A on 122/150 items; Q8 on 118, Q4 on 103, Q3 on 85, and Q2 on 149. The gold answer was A on 39/150 items. This strong letter bias and the low BF16 score limit interpretation: the >100% headline is an observed accuracy ratio under this forced-letter protocol, not evidence of general improvement. We preserved the preregistered prompt and scoring rather than tuning against these results. The Q4 rule is one-sided noninferiority (no loss greater than 2 pp), so a gain passes it.

## Reproduce
Run `source /workspace/tools/setup.sh`, install the build dependencies listed in scripts/setup_runtime.sh, then use `/workspace/tools/mlenv/bin/python scripts/prepare.py`. For the measured GPU configuration, use scripts/remote_worker.py in a Colab L4 runtime with the frozen results/items.json copied in; it installs the pinned CUDA wheel and downloads models. On the measured Colab image this first attempt failed before inference because CUDA 12 shared libraries were absent; execute scripts/remote_repair.py through colab exec afterward. That script installs nvidia-cuda-runtime-cu12 and nvidia-cublas-cu12, supplies their library directories in LD_LIBRARY_PATH, and runs all five formats in fresh processes. These two compatibility packages were not version-pinned; the model files and llama-cpp-python wheel version were pinned. For CPU reproduction use `scripts/run_all.sh`; after downloading GPU results, run `/workspace/tools/mlenv/bin/python scripts/analyze.py`. Existing prediction rows are skipped; each format runs in its own process. Model downloads are pinned and SHA-256 verified. The CPU pilot took 79.105 seconds for one 77-token BF16 prompt, projecting to 197.8 minutes for BF16 alone, so the permitted L4 fallback was used for all final measurements. Colab cost and shutdown evidence are in README.md and results/colab_usage_*.txt. The CPU pilot is preserved separately and excluded from the final paired comparison.

## Sources
- [Pinned public GGUF files](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/tree/50968a4468ef4233ed78cd7c3de230dd1d61a56b)
- [ARC-Easy public dataset](https://huggingface.co/datasets/allenai/ai2_arc)
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
