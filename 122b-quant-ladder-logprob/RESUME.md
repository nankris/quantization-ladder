# Completed experiment 122b

GPU evaluation and local publication work are complete. b10-122b was stopped successfully; results/stop.txt proves termination. Never restart inference for this completed run. No other session was stopped.

All five formats have 4,972 paired fresh rows. Frozen input and hypothesis checks pass (results/preregistration_audit.json). Retained recovery prefixes match their saved hashes. scripts/analyze.py reconstructs predictions from raw scores, checks IDs, excludes earlier/pilot questions, and computes the registered bootstrap intervals. Results and decision rules were not changed after seeing confirmation.

Overall DISPROVEN: Q4 -2.03 pp versus BF16, 95% CI [-2.80,-1.25], missing the fixed one-point non-inferiority margin. Q2 -40.99 pp, CI [-42.64,-39.36], passes the five-point degradation target. BF1679.93%, Q477.90%, Q238.94%. Full-text sensitivity and post hoc split checks are disclosed.

Publication: README.md, writeup.md, blog.md (1,616 words), three 150-dpi charts, table.png, diagram.png plus editable Excalidraw JSON, four termshot screenshots from real files/program output. All images visually inspected, no clipping/overlap. figures/colab_run.txt includes GPU, run, timing and shutdown excerpts. Conservative CU upper estimate2.34 across two L4 allocations; exact first release time unknown. Account balance change4.02 includes concurrent work and is not attributed entirely to this experiment. Initial55-minute estimate preserved; final timing.json includes actual elapsed time and stage definitions.

Reproduction commands are in scripts/README.md. No push. Final local commit contains artifacts. Any later scripts/finalize.py invocation recomputes publication elapsed time, so avoid rerunning it unless intentionally updating timing.
