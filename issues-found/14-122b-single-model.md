# 14 (122b): Single model

- **Experiment:** 122b (`122b-quant-ladder-logprob/`)
- **Found by:** an independent read-only review of the repo on 21 Oct 2026, 21:13-21:18 IST (fact sheet `122b-quant-ladder-logprob.md`). Numbers and paths below come from that review, which checked them against the repo's results files.

## Issue and evidence
Single model (0.6B, where quantization noise is proportionally large), single prompt, Unsloth imatrix quants (recipe confounded). One validation tolerance assertion failed (0.002 too strict; max letter-logit diff 0.027). Disclosed and benign.

## Status
Open, documented. Nothing in the results was changed because of it. The README/writeup or the Substack post states where it changes how the result should be read. Any fix needs a new pre-registered run on fresh data (hypothesis rules), not an edit to these numbers.
