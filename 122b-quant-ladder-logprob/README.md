# 122b: quantization ladder with likelihood scoring

## Question and evidence
Does the apparent Q4 improvement in experiment 122 survive correct likelihood extraction and option-position balancing? The earlier writeup reports exactly: “4-bit kept 126.7% of the accuracy at 33.1% of the size.” BF16 was 60/150 (40.00%), Q4 76/150 (50.67%), Q2 38/150 (25.33%). BF16 chose A 122/150 times, with gold A 39/150. This is evidence for investigating a scoring artifact, not evidence for a general quantization benefit.

Source artifacts: ../122-quantization-ladder/writeup.md and scripts/evaluate.py. Public source repository: https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/tree/50968a4468ef4233ed78cd7c3de230dd1d61a56b . Dataset: https://huggingface.co/datasets/allenai/ai2_arc .

## Preregistered hypotheses and fixed decisions
H1: Q4_K_M accuracy is within 1 percentage point of BF16 (one-sided non-inferiority). A deployment tradeoff of at most one extra wrong answer per 100 questions for a roughly threefold file reduction motivates the margin. PROVEN if the lower endpoint of a paired two-sided 95% bootstrap CI for Q4 minus BF16 is >= -1 pp; DISPROVEN if its upper endpoint is < -1 pp; otherwise INCONCLUSIVE.

H2: Q2_K drops at least 5 pp versus BF16. The earlier observed drop was 14.67 pp, making this a deliberately weaker replication target, representing at least five extra errors per 100. PROVEN if the upper endpoint of Q2 minus BF16 is <= -5 pp; DISPROVEN if its lower endpoint is > -5 pp; otherwise INCONCLUSIVE. Overall PROVEN only if both pass, DISPROVEN if either fails, else INCONCLUSIVE. No hypothesis changes after results.

Primary metric: item accuracy after four cyclic rotations of the four choices. For each rotation score the single tokens A/B/C/D using full-vocabulary next-token log probabilities. Map scores back to original answer identities and average log probabilities across rotations, then argmax (ties first original index). An additive letter preference cancels in this average. Keep the old prompt exactly, including disabled thinking. Save unrotated accuracy, per-rotation letter counts, and original-identity predictions as diagnostics. Full-vocabulary log-softmax and the logits give identical rankings within a prompt; logprob alone cannot cure bias.

Secondary: mean per-token log probability of each complete option text, without a terminal EOS, under a separate prompt asking for the answer text. Score all four completions in original order. This is a sensitivity check, not a replacement primary endpoint. Save token counts and token log probabilities. No generated reasoning, no paid API.

95% paired percentile bootstrap, 20,000 resamples, seed 1222026, resampling questions (never treating rotations as independent). Accuracy CIs also bootstrap questions. H1 and H2 are separate claims with an overall conjunction; descriptive ladder comparisons are not multiple new confirmatory claims.

## Sample sizing and pilot policy (before inference)
Use 32 four-choice ARC-Easy training items (seed 122032) as a disjoint feasibility/discordance pilot. Exclude all 150 earlier question IDs and all pilot IDs from confirmation across every split. Use the identical frozen dataset revision as 122: 210d026faf9955653af8916fad021475a3f00453. Deduplicate by ID and exact question text and exclude earlier/pilot question text too.

At true Q4 difference zero, approximate 80% power with a two-sided 95% lower bound for a 1 pp margin needs n = ceil((1.96+0.842)^2*q/0.01^2), where q is paired correctness discordance. Use max(0.02, pilot discordance) for planning; the floor avoids assuming perfect agreement from 32 examples. For q=0.10 this is 7,852 items, exceeding fresh ARC-Easy availability. Select min(needed, available) fresh items, with at least 1,000 when available; prefer the entire fresh pool when the requested n exceeds availability. Freeze exact n and report detectable margins after the pilot, BEFORE confirmation. A CI crossing the margin remains inconclusive; limited data does not justify relaxing it. Deterministic likelihood scoring needs no decoding seeds; inference repetitions are not independent questions.

## Setup and decisions
- Same Qwen3-0.6B and all five pinned Unsloth GGUF artifacts from 122: BF16, Q8_0, Q4_K_M, Q3_K_M, Q2_K. Copy manifest identity, verify SHA256 after download. Use fresh processes and GPU offload with llama-cpp-python 0.3.36 CUDA wheel, logits_all=True. Validate last-position logits against native output and prefix continuation against full-sequence scoring on pilot. Never reuse stale logits.
- NVIDIA L4, session b10-122b; hard cap 6 CU. Detached VM worker, append/flush rows, resume completed IDs, frequent downloads. Record package versions and nvidia-smi. Read daily floor immediately before allocation; check usage during work; stop session on completion/failure.
- Public HF data only. Local work only in this directory. Reading earlier run and operational instructions is required; never modify them.
- Decisions: use ARC-Easy across available splits to improve precision without recycling the earlier evaluation. This expands beyond the earlier test-only subset and will be disclosed. Any pilot-based sample amendment is recorded separately without rewriting hypotheses. Model/source/article claims are not substitutes for this replication.
- Planned estimate: 55 minutes (setup 12, GPU run 23, eval 8, writeup 12). Timing: estimated 55 minutes; actual/GPU CU to be recorded in results/timing.json at completion.

## Reproduction and outputs
Scripts and raw JSONL include complete scores, option mappings and served-model token counts. README is committed before pilot, then sample-size amendment committed before confirmation. Final deliverables include writeup.md, blog.md, results, charts, table rendering and editable Excalidraw pipeline. Local Git only; never push.

## Sample freeze before confirmation

The disjoint 32-item pilot had BF16 28/32 and Q4 25/32 correct under cyclic scoring, with paired correctness discordance 3/32 = 0.09375. The registered calculation requests 7361 items. Only 4972 fresh deduplicated ARC-Easy items exist, so confirmation uses all 4972. Approximate power at a true zero difference is 63.4%, and the approximate 80%-power margin is 1.22 pp. The fixed 1 pp hypothesis and CI decisions remain unchanged. Pilot results are not confirmation and suggest the non-inferiority prediction may fail. Exact frozen records: results/items.json and results/power.json.

## Runtime validation and resource update
The single pilot-question runtime probe produced the same winning letter with the original native `logits_all=False` path and the new `logits_all=True` scores. Letter logits differed by at most 0.0172 (full vocabulary max 0.0386). Incremental versus full-sequence evaluation gave the same full-vocabulary argmax; their max logit discrepancy was 0.1138 (letter candidates 0.0270), so an initial overly strict 0.002 tolerance assertion failed. Both log output and final measurements are retained. This is a limited numerical smoke check, not proof of equivalence on all questions; the primary evaluator consistently uses full-sequence scores and checks Python/native agreement on every rotation. These checks do not implicate a gross extraction error. Pre-registered hypotheses and scoring are unchanged.

Pilot end-to-end evaluation was 7-9 seconds per 32 questions per format. Extrapolated confirmatory GPU work is around 80-95 minutes, longer than the initial 23-minute GPU estimate; the estimate is retained for honest timing comparison. This remains comfortably within 6 CU at the observed L4 rate of 1.54 CU/hour. A detached remote watchdog limits work to 3.2 hours. All five pilot formats finished before confirmation started. No tuning uses confirmatory accuracy.

## Scheduling decision during confirmation
The initial serial worker occupied about 47% of the L4 (saved nvidia-smi evidence), while the host also computed log-softmax values. To keep the GPU busy and reduce idle billing, a second detached serial queue evaluates Q2, Q3, then Q4 on the same session/GPU while the original queue works from BF16 forward. A per-format exclusive file lock serializes writers when queues meet. This changes only scheduling, not inference settings, questions, scores or decision rules. Each format still loads in its own fresh process. Completion is declared only after the original queue has reached and validated/skipped all five formats. Original BF16 was already running before locks were introduced; the second queue never evaluates BF16. No throughput comparison is claimed under concurrency.

## CU accounting decision
The account initially had 105.75 CU and zero active assignments. This session alone reported 1.54 CU/hour. Later usage reports show two active assignments and 3.08 CU/hour, so an account balance difference cannot be attributed entirely to 122b. Report the account difference separately and estimate 122b's CU from allocation duration times the observed isolated 1.54 CU/hour rate, with roughly one minute of allocation timestamp uncertainty. Initial allocation was around 2026-10-19 21:52 UTC (preregistration commit and CLI creation completed in that minute). No other session is inspected or modified. The 6 CU ceiling is enforced conservatively by the runtime watchdog plus usage checks.

## Recovery decision

At 22:51 UTC the service reported no active sessions, so the original VM could not be reconnected. Resume the 22:27 local checkpoint on a replacement L4 under the same session name, retaining complete BF16/Q2 and partial Q8/Q3 rows. Do not change scoring or sample. Archive original runtime evidence in results/allocation1. Conservatively charge the first allocation from 21:52 through 22:51 (1.51 CU maximum at 1.54/hour); add replacement duration and stop before a combined 6 CU. The exact first release time is unknown.

## Decisions

Retain the registered ARC-Easy item split and same model rather than introduce a new dataset after confirmation started. The 32-item pilot and confirmation are disjoint by ID and exact question text, but both use ARC-Easy. This meets the requested fresh-item rerun and does not meet the general operational preference for a pilot on a different dataset/model; disclose that limit. Five decoding seeds would repeat deterministic scores and cannot substitute for more independent questions. Retain fixed margins despite the pilot's unfavorable Q4 result and the pool-size power shortfall. Original forced-letter scoring was next-token logit ranking, not sampled generation; log-softmax alone preserves its argmax. The principal correction is cyclic balancing.

## Final result

Q4 changed accuracy by -2.03 percentage points versus BF16 after option balancing. 95% paired CI: [-2.80, -1.25] pp. H1: DISPROVEN; H2: PROVEN; overall: DISPROVEN. The complete result and caveats are in writeup.md.

Timing: estimated 55 minutes; actual 94.4 minutes. GPU: NVIDIA L4. CU: 2.34 conservative duration-based upper estimate across two allocations × 1.54 CU/hour; account balance change 4.02 CU (may include concurrent work).

Screenshots (rendered from preserved files and program output): figures/screenshots/first.png, flaw.png, fixed.png, verdict.png. Input excerpts are results/screenshot_*.txt; renderer: scripts/screenshots.py.
