# 13 (rerun): Single model

- **Study:** the rotation-balanced rerun (`../quant-ladder-logprob/`)
- **Found by:** an independent read-only review of this repo on 21 Oct 2026. Numbers and paths below were checked against the repo's results files.

## Issue and evidence
Single model (0.6B, where quantization noise is proportionally large), single prompt, Unsloth imatrix quants (recipe confounded). One validation tolerance assertion failed (0.002 too strict; max letter-logit diff 0.027). Disclosed and benign.

## Status
Open, documented. Nothing in the results was changed because of it. The README and writeup state where it changes how the result should be read. Any fix needs a new preregistered run on fresh data, not an edit to these numbers.
