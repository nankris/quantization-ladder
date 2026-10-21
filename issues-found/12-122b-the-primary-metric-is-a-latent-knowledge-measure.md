# 12 (122b): The primary metric is a latent-knowledge measure,

- **Experiment:** 122b (`122b-quant-ladder-logprob/`)
- **Found by:** an independent read-only review of the repo on 21 Oct 2026, 21:13-21:18 IST (fact sheet `122b-quant-ladder-logprob.md`). Numbers and paths below come from that review, which checked them against the repo's results files.

## Issue and evidence
**The primary metric is a latent-knowledge measure,** not user-facing behavior (see the 59% stat). The full-text secondary is weak: ~40% for BF16, it uses unnormalized mean token logprob, and it is barely above the letter-biased baseline. It agrees in sign (-3.66) but isn't an independent validation.

## Status
Open, documented. Nothing in the results was changed because of it. The README/writeup or the Substack post states where it changes how the result should be read. Any fix needs a new pre-registered run on fresh data (hypothesis rules), not an edit to these numbers.
