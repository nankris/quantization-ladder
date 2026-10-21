# Quantization ladder

Quantization stores a model's weights using fewer bits, reducing file size and potentially changing its answers.

## Hypothesis and fixed decision rule (written before measurements)
For Qwen3-0.6B, Q4_K_M preserves ARC-Easy accuracy within 2 percentage points of F16 at approximately one third of its file size, while Q2_K loses more than 5 percentage points.

Use 150 fixed public ARC-Easy test items: sample without replacement with NumPy seed 122 from four-choice items, preserving sampled order. Freeze the items before any inference. Score each by the highest next-token logit among A/B/C/D after the same non-thinking chat prompt; no sampling, no free-form reasoning. Run identical prompts and scoring for F16, Q8_0, Q4_K_M, Q3_K_M (Q3 if necessary), Q2_K. This is constrained single-letter scoring, not full answer-text likelihood.

Paired item bootstrap: 20,000 resamples, seed 122, percentile 95% confidence intervals for accuracy differences versus F16 and for the accuracy ratio. Define delta = quantized accuracy minus F16 in percentage points. Q4 accuracy claim PROVEN if CI lower bound >= -2, DISPROVEN if CI upper bound < -2, otherwise INCONCLUSIVE. Q4 size claim passes if size is 25–40% of F16. Q2 degradation claim PROVEN if CI upper bound < -5, DISPROVEN if CI lower bound >= -5, otherwise INCONCLUSIVE. Overall hypothesis PROVEN only if both accuracy claims and size pass; DISPROVEN if any claim is disproven or size fails; otherwise INCONCLUSIVE. The headline reports observed Q4/F16 accuracy and file-size percentages regardless of verdict. No changing sample, prompt, model, or scoring after seeing accuracy.

## Setup
- CPU first, aarch64, two threads; model Qwen3-0.6B to respect approximately 7 GB RAM and 60-minute target.
- Prebuilt public Hugging Face GGUFs, preferably all from the same repository/revision. Record exact files, revisions, hashes, runtime version and data provenance in results.
- llama.cpp or llama-cpp-python. Same context and batch configuration for every format; fresh process per format. Record actual configuration.
- Measure actual file bytes and process peak resident RAM, including model and runtime, not just weights. Benchmark prompt and generation tokens/s with a common prompt and fixed generation count, separate from evaluation. Report cold/warm conditions and repetitions.
- Save every item's prediction and logits incrementally; resume by skipping completed items. Store raw outputs in results/; scripts in scripts/; generated model/build files excluded from Git.
- CPU pilot determines feasibility. Colab L4 allowed only if extrapolated CPU runtime exceeds remaining 60-minute budget; at most 2 CU, usage checked first, own session always stopped. No paid APIs.
- Final GPU: NVIDIA L4 (23,034 MiB), all layers offloaded. Total CU used: 0.28 by account balance difference; session stopped (see final run record below).

## Limitations planned in advance
150 items may be insufficient to establish a 2-point noninferiority margin. Results describe this small model, prompt, dataset subset, and machine; quantization formats have mixed precision and nominal bit widths are not exact file-size ratios. Forced letter scoring can underestimate unconstrained reasoning performance.

Preflight selection (before inference): the chosen repository provides BF16 rather than F16. Use BF16 as the 16-bit reference everywhere (the decision rules above referring to F16 apply to BF16). All five files come from unsloth/Qwen3-0.6B-GGUF revision 50968a4468ef4233ed78cd7c3de230dd1d61a56b. No runtime environment_status tool is exposed and no network-policy snapshot exists on this worker; inherited proxy configuration is used.

Runtime API check before inference: llama-cpp-python 0.3.36 leaves its Python `scores` buffer unfilled with `logits_all=False`; the evaluator reads the native context's final-token logits directly. The scoring rule is unchanged. Source distribution identity is in results/runtime_source.json.

CPU feasibility pilot: first frozen BF16 item (77 prompt tokens) required 79.105 seconds, projecting to 197.8 minutes for BF16's 150 items alone. Stopped the CPU pilot after saving its raw result under results/cpu_pilot/. This exceeds the 60-minute target, so use the explicitly permitted Colab L4 fallback (max 2 CU). All five final formats will run on that same GPU backend; the CPU pilot is excluded from final accuracy and speed comparisons. Scoring/sample/decision rule remain unchanged. Final GPU configuration and usage will be recorded below.

Resume note (2026-10-16): previous session had expired before results were retrieved. Account balance before the original allocation was 163.95 CU; balance on resume was 163.76 CU with no active assignments (0.19 CU consumed). Recreated only `tig122-quant-ladder` on L4 after `colab usage`; the remaining experiment allowance is 1.81 CU. The original frozen sample, prompt and decision rule are unchanged.

## Final run record
- All five formats completed 150/150 frozen items; validation checks IDs, gold labels, identical prompts, logits-to-answer scoring, aggregate accuracy, GPU identity and benchmark counts. Raw predictions and metrics are in results/.
- GPU: NVIDIA L4; CUDA 12.4 llama-cpp-python 0.3.36 wheel, Python 3.13.15 on x86_64 Colab. CUDA 12 runtime and cuBLAS compatibility packages were installed after a pre-inference missing-library error. Actual CUDA system information is in results/gpu_environment.json. Host CPU build provenance is separate in results/runtime_source.json.
- GPU execution after compatibility repair: 28.14 seconds for the worker, including all model loads, 750 items and four benchmark repetitions per format. Installation/downloads took longer; original CPU/build work and an expired session were resumed. CPU setup began around 13:08 UTC; final GPU results and shutdown were saved around 13:45 UTC on 2026-10-16 (roughly 37 minutes elapsed across attempts).
- CU: initial balance 163.95, resume 163.76, final 163.67 = **0.28 CU total** (rounded account readouts, 0.01 CU precision). Previous allocation 0.19; resumed allocation 0.09. Rate 1.54 CU/hour. No other active assignments reported at either endpoint.
- Shutdown: `colab stop -s tig122-quant-ladder` returned `Session terminated.` Final `colab usage` reports 0 active assignments and 0.00 CU/hour. Evidence: results/colab_stop.txt and results/colab_usage_after.txt.
- Verdict: **PROVEN under the preregistered constrained-scoring rule**. Q4 delta +10.67 pp [6.00, 16.00]; size 33.11%. Q2 delta −14.67 pp [−21.33, −8.00]. Headline: **4-bit kept 126.7% of the accuracy at 33.1% of the size.**
- Scope warning from observed results: BF16 chose A 122/150 times and Q2 149/150. The >100% ratio reflects this particular weak, letter-biased baseline; it is not a general claim that quantization improves model capability. The sample, prompt and rule were not changed after observing this.
