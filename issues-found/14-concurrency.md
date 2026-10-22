# 14 (rerun): Concurrency

- **Study:** the rotation-balanced rerun (`../quant-ladder-logprob/`)
- **Found by:** an independent read-only review of this repo on 21 Oct 2026. Numbers and paths below were checked against the repo's results files.

## Issue and evidence
Concurrency (two queues on one GPU) doesn't affect accuracy. No speed claims are made.

## Status
Open, documented. Nothing in the results was changed because of it. The README and writeup state where it changes how the result should be read. Any fix needs a new preregistered run on fresh data, not an edit to these numbers.
