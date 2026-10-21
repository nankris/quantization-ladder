# 11 (122b): Population change

- **Experiment:** 122b (`122b-quant-ladder-logprob/`)
- **Found by:** an independent read-only review of the repo on 21 Oct 2026, 21:13-21:18 IST (fact sheet `122b-quant-ladder-logprob.md`). Numbers and paths below come from that review, which checked them against the repo's results files.

## Issue and evidence
**Population change:** 122 used test only; 122b pools train/val/test. The ARC train split is very likely in pretraining or instruction data (contamination). The train-split delta (-2.91) is larger than test (-1.68) and validation (0.00); heterogeneity is disclosed post hoc. Test-only would be INCONCLUSIVE.

## Status
Open, documented. Nothing in the results was changed because of it. The README/writeup or the Substack post states where it changes how the result should be read. Any fix needs a new pre-registered run on fresh data (hypothesis rules), not an edit to these numbers.
