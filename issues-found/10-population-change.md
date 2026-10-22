# 10 (rerun): Population change

- **Study:** the rotation-balanced rerun (`../quant-ladder-logprob/`)
- **Found by:** an independent read-only review of this repo on 21 Oct 2026. Numbers and paths below were checked against the repo's results files.

## Issue and evidence
**Population change:** The original run used test only; the rerun pools train/val/test. The ARC train split is very likely in pretraining or instruction data (contamination). The train-split delta (-2.91) is larger than test (-1.68) and validation (0.00); heterogeneity is disclosed post hoc. Test-only would be INCONCLUSIVE.

## Status
Open, documented. Nothing in the results was changed because of it. The README and writeup state where it changes how the result should be read. Any fix needs a new preregistered run on fresh data, not an edit to these numbers.
