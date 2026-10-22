# 01 (original run): Broken metric: forced-letter logit argmax with severe position bias

- **Study:** the original run (`../original-run/`)
- **Found by:** an independent read-only review of this repo on 21 Oct 2026. Numbers and paths below were checked against the repo's results files.

## Issue and evidence
**Broken metric: forced-letter logit argmax with severe position bias.** BF16 picks A 81% of the time (122/150), Q2 99% (149/150), and Q3 shifts its bias to D. BF16 at 40% on ARC-Easy is far below what this model's latent ranking supports (~72-80% once debiased, confirmed by the rerun's 79.9%). The headline measures *how much each quant weakens the A-preference*, not retained capability. The writeup acknowledges the bias in a "scope warning" but still headlines "126.7%" and PROVEN.

## Status
Open, documented. Nothing in the results was changed because of it. The README and writeup state where it changes how the result should be read. Any fix needs a new preregistered run on fresh data, not an edit to these numbers.
