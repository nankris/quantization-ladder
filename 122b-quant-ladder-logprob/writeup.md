# Letter balancing changes the quantization ladder

**Q4 changed accuracy by -2.03 percentage points versus BF16 after option balancing.**

Overall verdict: **DISPROVEN**. Q4 within 1 pp: **DISPROVEN**. Q2 drop >=5 pp: **PROVEN**. These decisions use the fixed cyclic letter endpoint, not whichever score looks best.

| Format | Original letters % | Cyclic letters % (95% CI) | Δ vs BF16, pp (95% CI) | Full text % |
|---|---:|---:|---:|---:|
| BF16 | 39.42 | 79.93 [78.80, 81.03] | +0.00 [+0.00, +0.00] | 40.35 |
| Q8_0 | 40.14 | 79.55 [78.40, 80.65] | -0.38 [-0.76, +0.00] | 39.98 |
| Q4_K_M | 48.93 | 77.90 [76.73, 79.02] | -2.03 [-2.80, -1.25] | 36.69 |
| Q3_K_M | 43.91 | 74.34 [73.11, 75.54] | -5.59 [-6.66, -4.53] | 35.70 |
| Q2_K | 24.92 | 38.94 [37.57, 40.31] | -40.99 [-42.64, -39.36] | 30.75 |


## Two-sentence takeaway
On 4,972 fresh science questions, Q4 scored 77.90% and BF16 79.93% after averaging answer-letter likelihoods across all four cyclic option rotations. The old apparent Q4 advantage depended strongly on the original answer format, so a forced-letter win should not be read as a general improvement in capability.

## Method and interpretation
The same pinned Qwen3-0.6B GGUF weights as experiment 122 were loaded in fresh processes on NVIDIA L4 using llama-cpp-python 0.3.36, context 2048, batch 512, microbatch 128, GPU layers 99, two CPU threads, flash attention disabled, logits_all=True. All model hashes were verified. The first VM disappeared; complete BF16/Q2 and partial Q8/Q3 checkpoints were retained and missing rows finished on a replacement L4. Original allocation evidence is archived in results/allocation1; results/recovery.json records retained row counts. Per-format metadata seconds for resumed formats measure only work since the last process start, not total runtime. Four single-token letter log probabilities are scored against the full vocabulary after the exact original non-thinking chat prompt. For each question, four cyclic permutations place every content answer in every letter position. We map scores back to original answer identities, average log probabilities, and pick the largest. This cancels a fixed additive preference for a letter; it does not guarantee invariance to content-dependent ordering effects. Within a prompt logits and log probabilities give the same ranking. This was likelihood ranking in 122 too, rather than sampled free-form generation.

Secondary full-text scoring replaces the instruction with “Reply with only the exact answer text.” Each candidate is tokenized without BOS, appended to the separately tokenized prompt, and teacher-forced in a reset context. Score the mean full-vocabulary log probability per candidate token; no EOS likelihood. Text prompt and candidate scores are a different metric, not another independent replication. Model token IDs, candidate token log probabilities, prompt-token counts, candidate counts and zero generated tokens are retained in every raw row. Prompt counts include repeated prefixes in the four full-text candidate evaluations. Letter candidates are scored from a common distribution, not fed as generated inputs.

Data: pinned allenai/ai2_arc ARC-Easy, revision 210d026faf9955653af8916fad021475a3f00453. The 4,972 confirmatory questions span splits {'test': 2203, 'train': 2203, 'validation': 566}. Exclude all 150 earlier IDs/question strings, all 32 pilot IDs/question strings, and exact duplicate question text. These items are fresh to this experiment, not guaranteed absent from model training. Pilot discordance 3/32 implied 7,361 items for approximately 80% power at true zero Q4 difference, versus 4,972 available; planned power was 63.4%. Deterministic inference seeds do not create independent data. Question-level paired bootstrap, 20,000 resamples, seed 1222026. For binary accuracy differences the implementation draws multinomial counts of the paired outcome categories, mathematically equivalent to resampling items. No independent-rotation bootstrap or significance fishing.

Predicted letter counts (original order):

| Format | A | B | C | D |
|---|---:|---:|---:|---:|
| BF16 | 4174 | 243 | 84 | 471 |
| Q8_0 | 4128 | 264 | 91 | 489 |
| Q4_K_M | 3447 | 546 | 165 | 814 |
| Q3_K_M | 2669 | 106 | 147 | 2050 |
| Q2_K | 4902 | 22 | 11 | 37 |

Secondary full-text Q4 minus BF16: -3.66 pp, 95% paired CI [-4.49, -2.84] pp. These secondary intervals are descriptive.

Gold counts: {'D': 1163, 'B': 1260, 'A': 1242, 'C': 1307}. Every rotation's output-letter counts and debiased original-answer identity counts appear in results/summary.json and results/predicted_letters.csv. Original-order accuracy is 39.42% BF16 versus 48.93% Q4. That paired, fresh-data comparison is more informative about scorer sensitivity than comparing the new sample directly with the old 150.

Across all formats, the model tokenizer recorded 16,554,025 evaluated input tokens and 878,850 scored candidate tokens, with zero generated tokens. Candidate totals include the letter scores drawn from each distribution; they are not all additional input tokens. See results/token_counts.json for per-format accounting.

Post hoc split sensitivity (not new confirmatory tests): Q4 minus BF16 was -2.91 pp on train (n=2,203; CI [-4.09, -1.77]), 0.00 pp on validation (n=566; CI [-2.12, +2.12]), and -1.68 pp on the fresh test split (n=2,203; CI [-2.86, -0.54]). Test-only is inconclusive at the one-point margin; the registered decision uses all 4,972 questions. Full descriptive results are in results/descriptive_split_checks.json.

## Caveats
One small model, one science benchmark family, one prompt per scoring style, prebuilt mixed-precision quantizers. This does not estimate a universal bit-width effect or test generated reasoning. Combining train, validation and test questions improves precision but expands beyond the earlier test-only distribution. No five-seed training replication applies to deterministic fixed-weight scoring. The small pilot gives an uncertain discordance estimate. Pilot and confirmation use disjoint ARC-Easy items, rather than a different dataset/model as preferred by the general operational rule. Bootstrap intervals describe item sampling, not prompt choice or unknown training contamination. Native/Python logit agreement is checked for all letter rotations; a one-question old/new and incremental/full smoke check showed small numerical differences and the same winning tokens, not universal equivalence. A first overly strict validation tolerance failed and is retained in logs. Exact-text deduplication does not remove semantic near duplicates. The follow-up context allocation is 2048 tokens, versus 1024 in 122; letter prompt content is unchanged. No new speed or memory superiority claim is made.

Timing: estimated 55 minutes; actual 94.4 minutes. GPU: NVIDIA L4. CU: 2.34 conservative duration-based upper estimate across two allocations × 1.54 CU/hour; account balance change 4.02 CU (may include concurrent work).

Publication assets: figures/accuracy.png, figures/deltas.png, figures/letter_distribution.png, figures/table.png, figures/diagram.png and editable diagram.excalidraw. Run proof: figures/colab_run.txt. Scripts resume by completed IDs; scripts/monitor.py retrieves checkpoints. Reproduction starts with scripts/prepare.py on the GPU and uses the frozen results/items.json; do not rerun the pilot to pick a different sample. Source: [pinned GGUF repository](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/tree/50968a4468ef4233ed78cd7c3de230dd1d61a56b), [ARC dataset](https://huggingface.co/datasets/allenai/ai2_arc), and results/earlier_writeup.md.
