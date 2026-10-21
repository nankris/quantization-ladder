# 03 (122): n=150 is underpowered for a 2 pp margin

- **Experiment:** 122 (`122-quantization-ladder/`)
- **Found by:** an independent read-only review of the repo on 21 Oct 2026, 21:13-21:18 IST (fact sheet `122-quantization-ladder.md`). Numbers and paths below come from that review, which checked them against the repo's results files.

## Issue and evidence
**n=150 is underpowered for a 2 pp margin** (the CI width on the delta is ~10 pp; the README admits it). It only "worked" because the spurious effect was huge.

## Status
Open, documented. Nothing in the results was changed because of it. The README/writeup or the Substack post states where it changes how the result should be read. Any fix needs a new pre-registered run on fresh data (hypothesis rules), not an edit to these numbers.
