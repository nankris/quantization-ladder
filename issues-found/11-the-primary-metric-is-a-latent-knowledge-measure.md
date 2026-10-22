# 11 (rerun): The primary metric is a latent-knowledge measure,

- **Study:** the rotation-balanced rerun (`../quant-ladder-logprob/`)
- **Found by:** an independent read-only review of this repo on 21 Oct 2026. Numbers and paths below were checked against the repo's results files.

## Issue and evidence
**The primary metric is a latent-knowledge measure,** not user-facing behavior (see the 59% stat). The full-text secondary is weak: ~40% for BF16, it uses unnormalized mean token logprob, and it is barely above the letter-biased baseline. It agrees in sign (-3.66) but isn't an independent validation.

## Status
Open, documented. Nothing in the results was changed because of it. The README and writeup state where it changes how the result should be read. Any fix needs a new preregistered run on fresh data, not an edit to these numbers.
