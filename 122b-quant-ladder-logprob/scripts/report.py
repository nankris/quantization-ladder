"""Render final prose from validated summary; inspect prose and figures before commit."""
import json,datetime,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]; s=json.loads((R/'results/summary.json').read_text()); a=s['summary']; bf,q8,q4,q3,q2=a; n=s['n']
def interval(r,m='cyclic'): return '['+', '.join(f'{x:+.2f}' for x in r[m+'_delta_ci'])+']'
def delta(r): return f'{r["cyclic_delta"]:+.2f}'
headline=f'Q4 changed accuracy by {delta(q4)} percentage points versus BF16 after option balancing.'
verb='lost' if q4['cyclic_delta']<0 else 'gained'; absd=abs(q4['cyclic_delta'])
timing=json.loads((R/'results/timing.json').read_text()); cost=json.loads((R/'results/cost.json').read_text())
timeline=f'Timing: estimated {timing["estimated_minutes"]} minutes; actual {timing["actual_minutes"]:.1f} minutes. GPU: NVIDIA L4. CU: {cost["session_cu_estimate"]:.2f} conservative duration-based upper estimate across two allocations × 1.54 CU/hour; account balance change {cost["account_balance_delta"]:.2f} CU (may include concurrent work).'
table='| Format | Original letters % | Cyclic letters % (95% CI) | Δ vs BF16, pp (95% CI) | Full text % |\n|---|---:|---:|---:|---:|\n'
for r in a:
 table+=f'| {r["format"]} | {r["unrotated_accuracy"]:.2f} | {r["cyclic_accuracy"]:.2f} [{r["cyclic_ci"][0]:.2f}, {r["cyclic_ci"][1]:.2f}] | {delta(r)} {interval(r)} | {r["text_accuracy"]:.2f} |\n'
text=f'''# Letter balancing changes the quantization ladder

**{headline}**

Overall verdict: **{s['verdict']}**. Q4 within 1 pp: **{s['H1_Q4']}**. Q2 drop >=5 pp: **{s['H2_Q2']}**. These decisions use the fixed cyclic letter endpoint, not whichever score looks best.

{table}

## Two-sentence takeaway
On {n:,} fresh science questions, Q4 scored {q4['cyclic_accuracy']:.2f}% and BF16 {bf['cyclic_accuracy']:.2f}% after averaging answer-letter likelihoods across all four cyclic option rotations. The old apparent Q4 advantage depended strongly on the original answer format, so a forced-letter win should not be read as a general improvement in capability.

## Method and interpretation
The same pinned Qwen3-0.6B GGUF weights as experiment 122 were loaded in fresh processes on NVIDIA L4 using llama-cpp-python 0.3.36, context 2048, batch 512, microbatch 128, GPU layers 99, two CPU threads, flash attention disabled, logits_all=True. All model hashes were verified. The first VM disappeared; complete BF16/Q2 and partial Q8/Q3 checkpoints were retained and missing rows finished on a replacement L4. Original allocation evidence is archived in results/allocation1; results/recovery.json records retained row counts. Per-format metadata seconds for resumed formats measure only work since the last process start, not total runtime. Four single-token letter log probabilities are scored against the full vocabulary after the exact original non-thinking chat prompt. For each question, four cyclic permutations place every content answer in every letter position. We map scores back to original answer identities, average log probabilities, and pick the largest. This cancels a fixed additive preference for a letter; it does not guarantee invariance to content-dependent ordering effects. Within a prompt logits and log probabilities give the same ranking. This was likelihood ranking in 122 too, rather than sampled free-form generation.

Secondary full-text scoring replaces the instruction with “Reply with only the exact answer text.” Each candidate is tokenized without BOS, appended to the separately tokenized prompt, and teacher-forced in a reset context. Score the mean full-vocabulary log probability per candidate token; no EOS likelihood. Text prompt and candidate scores are a different metric, not another independent replication. Model token IDs, candidate token log probabilities, prompt-token counts, candidate counts and zero generated tokens are retained in every raw row. Prompt counts include repeated prefixes in the four full-text candidate evaluations. Letter candidates are scored from a common distribution, not fed as generated inputs.

Data: pinned allenai/ai2_arc ARC-Easy, revision 210d026faf9955653af8916fad021475a3f00453. The {n:,} confirmatory questions span splits {s['split_counts']}. Exclude all 150 earlier IDs/question strings, all 32 pilot IDs/question strings, and exact duplicate question text. These items are fresh to this experiment, not guaranteed absent from model training. Pilot discordance 3/32 implied 7,361 items for approximately 80% power at true zero Q4 difference, versus 4,972 available; planned power was 63.4%. Deterministic inference seeds do not create independent data. Question-level paired bootstrap, 20,000 resamples, seed 1222026. For binary accuracy differences the implementation draws multinomial counts of the paired outcome categories, mathematically equivalent to resampling items. No independent-rotation bootstrap or significance fishing.

Predicted letter counts (original order):

| Format | A | B | C | D |
|---|---:|---:|---:|---:|
'''
for r in a: text+='| '+r['format']+' | '+' | '.join(str(r['unrotated_counts'].get(c,0)) for c in 'ABCD')+' |\n'
text+=f'''
Secondary full-text Q4 minus BF16: {q4['text_delta']:+.2f} pp, 95% paired CI {interval(q4,'text')} pp. These secondary intervals are descriptive.

Gold counts: {s['gold_counts']}. Every rotation's output-letter counts and debiased original-answer identity counts appear in results/summary.json and results/predicted_letters.csv. Original-order accuracy is {bf['unrotated_accuracy']:.2f}% BF16 versus {q4['unrotated_accuracy']:.2f}% Q4. That paired, fresh-data comparison is more informative about scorer sensitivity than comparing the new sample directly with the old 150.

Across all formats, the model tokenizer recorded {sum(r['evaluated_input_tokens'] for r in a):,} evaluated input tokens and {sum(r['candidate_tokens'] for r in a):,} scored candidate tokens, with zero generated tokens. Candidate totals include the letter scores drawn from each distribution; they are not all additional input tokens. See results/token_counts.json for per-format accounting.

Post hoc split sensitivity (not new confirmatory tests): Q4 minus BF16 was -2.91 pp on train (n=2,203; CI [-4.09, -1.77]), 0.00 pp on validation (n=566; CI [-2.12, +2.12]), and -1.68 pp on the fresh test split (n=2,203; CI [-2.86, -0.54]). Test-only is inconclusive at the one-point margin; the registered decision uses all 4,972 questions. Full descriptive results are in results/descriptive_split_checks.json.

## Caveats
One small model, one science benchmark family, one prompt per scoring style, prebuilt mixed-precision quantizers. This does not estimate a universal bit-width effect or test generated reasoning. Combining train, validation and test questions improves precision but expands beyond the earlier test-only distribution. No five-seed training replication applies to deterministic fixed-weight scoring. The small pilot gives an uncertain discordance estimate. Pilot and confirmation use disjoint ARC-Easy items, rather than a different dataset/model as preferred by the general operational rule. Bootstrap intervals describe item sampling, not prompt choice or unknown training contamination. Native/Python logit agreement is checked for all letter rotations; a one-question old/new and incremental/full smoke check showed small numerical differences and the same winning tokens, not universal equivalence. A first overly strict validation tolerance failed and is retained in logs. Exact-text deduplication does not remove semantic near duplicates. The follow-up context allocation is 2048 tokens, versus 1024 in 122; letter prompt content is unchanged. No new speed or memory superiority claim is made.

{timeline}

Publication assets: figures/accuracy.png, figures/deltas.png, figures/letter_distribution.png, figures/table.png, figures/diagram.png and editable diagram.excalidraw. Run proof: figures/colab_run.txt. Scripts resume by completed IDs; scripts/monitor.py retrieves checkpoints. Reproduction starts with scripts/prepare.py on the GPU and uses the frozen results/items.json; do not rerun the pilot to pick a different sample. Source: [pinned GGUF repository](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/tree/50968a4468ef4233ed78cd7c3de230dd1d61a56b), [ARC dataset](https://huggingface.co/datasets/allenai/ai2_arc), and results/earlier_writeup.md.
'''
(R/'writeup.md').write_text(text)
if s['H1_Q4']=='DISPROVEN': interpretation='My one-point Q4 promise failed. The entire confidence interval was below the tolerance I had written down before the run.'
elif s['H1_Q4']=='INCONCLUSIVE': interpretation='My one-point Q4 promise remains unproven. The interval crosses the tolerance I wrote down, so a plausible point estimate cannot settle it.'
else: interpretation='The one-point Q4 non-inferiority prediction passed on this benchmark. That supports this specific deployment tradeoff, not the old claim that compression improved general capability.'
q2interpret={'PROVEN':'The Q2 degradation prediction passed.','DISPROVEN':'The Q2 degradation prediction failed.','INCONCLUSIVE':'The Q2 degradation prediction remains inconclusive.'}[s['H2_Q2']]
blog=f'''# Q4 {verb} {absd:.2f} points once I balanced the answer letters

A quantization result that looked like an improvement was also a test of how much a model liked the letter A.

The popular promise is that four-bit models preserve quality while taking much less space. The [GPTQ paper](https://arxiv.org/abs/2210.17323) describes “negligible accuracy degradation” for its own models and quantization method. That is an attractive engineering trade: fit a model on cheaper hardware without paying much in wrong answers. It is not a guarantee for every model or every scoring script.

My headline from this rerun is **{delta(q4)} percentage points for Q4 versus BF16**, after balancing the option letters. That is the number I would carry forward, with its uncertainty, rather than my first run's apparent improvement.

## What I expected, and what the first run said

I expected moderate compression to preserve most accuracy and aggressive compression to hurt. For this follow-up I registered two concrete claims: Q4 would stay within one percentage point of BF16, and Q2 would lose at least five points. One extra mistake per hundred questions was my practical Q4 tolerance.

The [earlier writeup](results/earlier_writeup.md) sounded much better than that: “4-bit kept 126.7% of the accuracy at 33.1% of the size.” Its table recorded BF16 at 40.00%, Q4 at 50.67%, and Q2 at 25.33%. Those were 60, 76, and 38 correct answers out of 150. The reported Q4 difference was +10.67 percentage points, with a paired interval of [6.00, 16.00].

![The first result as preserved in its writeup](figures/screenshots/first.png)

The archived writeup reported a Q4 gain and a passing verdict.

I am preserving those numbers because the correction is the story. Replacing them with the rerun would hide why I needed another experiment.

## Why I got suspicious

BF16 predicted A on 122/150 items. The gold answer was A on only 39/150. Q2 chose A on 149/150. Q4 chose A less often, on 103/150, and scored better.

![Evidence of the letter bias](figures/screenshots/flaw.png)

The original writeup recorded the predicted-letter counts and the mismatched gold distribution.

Imagine a model that understands a question but also gives a large bonus to the first answer label. A weight change that weakens that bonus can improve a multiple-choice score without improving the underlying science knowledge. A leaderboard can accidentally reward a different formatting preference.

That pattern does not prove that every extra Q4 answer came from letter bias. It does make a broad claim about improved capability hard to defend. I needed a test where each answer took a turn wearing each letter.

## The flaw, and the fix

There is an easy but ineffective repair here: replace raw logits with log probabilities and call the measurement corrected. Within one prompt, that changes the scale and leaves the winning letter unchanged. The first experiment was already ranking letter logits, not sampling long answers. There was no decoding randomness to average away.

I kept its letter prompt and used four cyclic rotations. If the original options were A, B, C, D, the next version moved the first option to the end. After four versions, every content answer had occupied every position.

For each version I measured the probability of A, B, C, and D as the next token. I mapped those scores back to the original answer texts and averaged their log probabilities. A fixed additive preference for A then contributes equally to every answer. More complicated interactions with option order can survive, so I call this balancing rather than a universal cure.

![The evaluation pipeline](figures/diagram.png)

The diagram shows the two scoring paths. Four rotations produce one primary answer per question; a separate full-text check asks whether the conclusion depends on predicting a letter at all.

## What I tested

I used Qwen3-0.6B in exactly the five [pinned Unsloth GGUF formats](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/tree/50968a4468ef4233ed78cd7c3de230dd1d61a56b) from the first experiment: BF16, Q8_0, Q4_K_M, Q3_K_M, and Q2_K. All ran on NVIDIA L4 GPUs, one allocation at a time, with llama-cpp-python 0.3.36 and the same non-thinking chat structure. Downloaded weight hashes were verified. The first VM disappeared; I resumed its saved rows on a replacement L4.

A disjoint pilot used 32 ARC-Easy training questions. BF16 got 28 correct after balancing, Q4 got 25. Their correctness disagreed on three questions. That implied roughly 7,361 questions for 80% power to establish the one-point margin if the true gap were zero.

There were only 4,972 fresh, deduplicated four-choice ARC-Easy questions available across the public training, validation, and test splits after exclusions. I used all of them. That gives about 63% planned power, not 80%. I committed the sample and that shortfall before confirmation. The earlier 150 questions and the pilot stayed out.

The secondary check scored each complete answer text by its average token log probability, using an instruction requesting the exact answer text. It is a different prompt and metric, not an interchangeable estimate of the primary result. Raw records include actual model token IDs, token scores, and counts. No paid model judged the answers.

## The real answer

BF16 reached {bf['cyclic_accuracy']:.2f}% on the balanced score. Q4 reached {q4['cyclic_accuracy']:.2f}%, a difference of {delta(q4)} points with a 95% paired interval of {interval(q4)}. Q8 reached {q8['cyclic_accuracy']:.2f}%, Q3 {q3['cyclic_accuracy']:.2f}%, and Q2 {q2['cyclic_accuracy']:.2f}%.

![Accuracy depends on the scoring path](figures/accuracy.png)

This chart puts the original-order letters, balanced letters, and full answer texts on the same fresh questions. Their disagreement is part of the result, not a reason to pick the most flattering line.

On original-order letters, BF16 scored {bf['unrotated_accuracy']:.2f}% and Q4 {q4['unrotated_accuracy']:.2f}%. BF16 chose A {bf['unrotated_counts'].get('A',0):,}/{n:,} times; Q4 chose it {q4['unrotated_counts'].get('A',0):,}/{n:,} times. With full answer-text likelihood, they scored {bf['text_accuracy']:.2f}% and {q4['text_accuracy']:.2f}%. The label-free check does not magically become ground truth; token normalization and instruction following matter too. BF16's roughly forty-point jump between original and balanced letters is itself a warning: the evaluator is a major part of what this benchmark measures.

![Predicted letter distributions](figures/letter_distribution.png)

Balancing the score does not force the model to predict A, B, C, and D equally often. This chart shows the physical output letters before mapping them back to answer identities, including preferences that remain across rotations.

![The preregistered margins and paired intervals](figures/deltas.png)

The intervals resample whole questions, keeping BF16 and each quantized result paired. The vertical reference lines mark the original one-point Q4 tolerance and five-point Q2 degradation target.

{interpretation} {q2interpret} Q2's balanced difference was {delta(q2)} points, with interval {interval(q2)}. The overall registered verdict is {s['verdict']}.

![Output from the fixed comparison](figures/screenshots/fixed.png)

These are the three scoring methods on the same fresh questions.

![Final registered statistics](figures/screenshots/verdict.png)

The program applies the original margins to paired confidence intervals.

## What surprised me, and what I got wrong

The mistake was treating a passing statistical rule on a biased measurement as a broad engineering conclusion. The first writeup did flag letter bias. That caveat did not turn the headline into a clean comparison of capability. The first run's confidence interval measured sampling uncertainty under its scorer. It did not test whether the scorer was measuring what I wanted.

I also underestimated the sample size needed for a one-point promise. Thousands of questions can still leave an awkward interval when the models disagree on enough individual items. More decoding seeds would not fix that here: these are deterministic likelihood comparisons on fixed weights.

The runtime checks did not reveal a gross logit-extraction failure. The old and new extraction paths selected the same letter on a pilot probe, with small numerical differences. An initially overstrict numerical tolerance failed, and that failure remains in the logs. The corrective evidence is the fresh scoring comparison, not a story about a conveniently broken library.

## What I would do in production

1. Log predicted-label frequencies alongside accuracy. Compare them with the gold distribution before discussing a quantization win.
2. Rotate option positions on an audit slice. Map predictions back to answer identities, and keep all rotations of one question together in statistical analysis.
3. Set the acceptable error increase before testing. Calculate the needed paired sample size rather than assuming a few hundred examples can resolve one point.
4. Evaluate the exact interaction users will see. A letter-ranking benchmark and generated answers exercise different behavior; neither should silently stand in for the other.

## Limitations

This is one small model on school science questions, with prebuilt mixed-precision GGUF artifacts. It does not isolate bit width from the quantization recipe, establish general reasoning quality, or prove the questions were absent from model training. Fresh means unused by these experiments.

Using all dataset splits improved precision but changed the population from the earlier test-only sample. Exact deduplication does not remove every paraphrase. Four rotations remove a simple position preference, not every ordering effect. The pilot and confirmation were disjoint items from the same benchmark, not a cross-dataset replication. The confidence intervals cover question sampling, not all those choices.

A post hoc check of the fresh test split alone gave Q4 a -1.68-point difference, with interval [-2.86, -0.54]. That subset is too imprecise to decide the one-point margin; it does not replace the registered full-pool result.

The useful habit is to inspect what a score rewards before deciding what a smaller model preserved.

Code: <repo link placeholder>
'''
(R/'blog.md').write_text(blog)
print('blog words',len(re.findall(r"\b[\w'-]+\b",blog)))
assert '\u2014' not in blog
readme=R/'README.md'
readme.write_text(readme.read_text().split('\n## Final result\n')[0])
with readme.open('a') as f:
 f.write(f'\n## Final result\n\n{headline} 95% paired CI: {interval(q4)} pp. H1: {s["H1_Q4"]}; H2: {s["H2_Q2"]}; overall: {s["verdict"]}. The complete result and caveats are in writeup.md.\n\n{timeline}\n')

with readme.open('a') as f:
 f.write('\nScreenshots (rendered from preserved files and program output): figures/screenshots/first.png, flaw.png, fixed.png, verdict.png. Input excerpts are results/screenshot_*.txt; renderer: scripts/screenshots.py.\n')
