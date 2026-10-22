# 08 (rerun): Verdict hinges on the margin choice

- **Study:** the rotation-balanced rerun (`../quant-ladder-logprob/`)
- **Found by:** an independent read-only review of this repo on 21 Oct 2026. Numbers and paths below were checked against the repo's results files.

## Issue and evidence
**Verdict hinges on the margin choice.** 1 pp is tighter than the original run's 2 pp; the point estimate -2.03 sits right at the old margin. The honest framing is "Q4 loses ~2 pp (1.25-2.8)", and DISPROVEN vs INCONCLUSIVE is a function of the threshold. The blog says "The vertical reference lines mark the original one-point Q4 tolerance". "Original" is misleading, since the original run used 2 pp. (The blog wording has since been corrected.)

## Status
Open, documented. Nothing in the results was changed because of it. The README and writeup state where it changes how the result should be read. Any fix needs a new preregistered run on fresh data, not an edit to these numbers.
