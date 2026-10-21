# 01 (122): Broken metric: forced-letter logit argmax with severe position bias

- **Experiment:** 122 (`122-quantization-ladder/`)
- **Found by:** an independent read-only review of the repo on 21 Oct 2026, 21:13-21:18 IST (fact sheet `122-quantization-ladder.md`). Numbers and paths below come from that review, which checked them against the repo's results files.

## Issue and evidence
**Broken metric: forced-letter logit argmax with severe position bias.** BF16 picks A 81% of the time (122/150), Q2 99% (149/150), and Q3 shifts its bias to D. BF16 at 40% on ARC-Easy is far below what this model's latent ranking supports (~72-80% once debiased, confirmed by 122b's 79.9%). The headline measures *how much each quant weakens the A-preference*, not retained capability. The writeup acknowledges the bias in a "scope warning" but still headlines "126.7%" and PROVEN.

## Status
Open, documented. Nothing in the results was changed because of it. The README/writeup or the Substack post states where it changes how the result should be read. Any fix needs a new pre-registered run on fresh data (hypothesis rules), not an edit to these numbers.
