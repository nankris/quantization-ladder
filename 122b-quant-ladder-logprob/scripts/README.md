# Reproduction and recovery

Use the frozen `results/items.json`, `pilot.json`, `manifest.json` and the committed README. Do not resample based on observed results. The sample-size amendment was committed as a8c729c before confirmation. The first protocol was committed before the pilot (see git history).

GPU execution used a detached worker on the experiment's Colab L4. `launch.py` installs/starts `worker.py` under `/content/b10-122b`. `prepare.py` verifies model file hashes and prepares data. `evaluate.py FORMAT confirm` appends and flushes scored rows, skips completed IDs, and locks each output format. `auxiliary.py` is a second serial queue on that same GPU, never another session. Dependencies and GPU evidence are in results/packages.txt and figures/colab_run.txt. The first VM was lost; `recovery_control.py` describes the replacement controller. Retained row hashes are checked during analysis.

The existing results need no GPU to analyze. From this experiment directory:

```sh
source /workspace/tools/setup.sh
/workspace/tools/mlenv/bin/python scripts/audit_prereg.py
/workspace/tools/mlenv/bin/python scripts/analyze.py > results/analysis_output.txt
/workspace/tools/mlenv/bin/python scripts/finalize.py > results/finalization_output.txt
/workspace/tools/mlenv/bin/python scripts/report.py
/workspace/tools/mlenv/bin/python scripts/screenshots.py > results/screenshots_output.txt
/workspace/tools/mlenv/bin/python scripts/verify.py
```

`finalize.py` recalculates publication elapsed time, so running it later changes timing.json, not the predictions or verdict. It requires saved successful shutdown evidence. `monitor.py` is the local checkpoint downloader and stops only b10-122b on completion/error or the conservative budget threshold. Remote GPU processes do not depend on it staying alive. Restart the local monitor after a sandbox reboot, without starting new inference if the job still runs.

Excalidraw source is figures/diagram.excalidraw. The diagram PNG was already rendered before recovery and inspected after recovery; the current control VM lacks /workspace/tools/excalidraw. Screenshot source excerpts are program-generated directly from the archived writeup and final statistics, via the shared termshot.py renderer.
