import json,csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
formats=['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']
items=json.loads((ROOT/'results/items.json').read_text()); ids=[x['id'] for x in items]
ys={}; metrics={}
for fmt in formats:
 rows=[json.loads(s) for s in (ROOT/f'results/predictions_{fmt}.jsonl').read_text().splitlines()]
 assert len(rows)==150 and len({x['id'] for x in rows})==150
 rows={x['id']:x for x in rows}; assert set(rows)==set(ids)
 ys[fmt]=np.array([rows[i]['correct'] for i in ids]); metrics[fmt]=json.loads((ROOT/f'results/metrics_{fmt}.json').read_text())
rng=np.random.default_rng(122); boot=rng.integers(0,150,(20000,150)); ref=ys['BF16']; refboot=ref[boot].mean(1)
summary=[]
for fmt in formats:
 y=ys[fmt]; m=metrics[fmt]; delta=(y-ref)[boot].mean(1)*100
 ratio=y[boot].mean(1)/refboot*100
 bench=[x for x in m['benchmark'] if not x['warmup']]
 row=dict(format=fmt,n=150,correct=int(y.sum()),accuracy_pct=y.mean()*100,accuracy_ci=np.quantile(y[boot].mean(1)*100,[.025,.975]).tolist(),delta_pp=float((y-ref).mean()*100),delta_ci=np.quantile(delta,[.025,.975]).tolist(),retained_accuracy_pct=y.mean()/ref.mean()*100,retention_ci=np.quantile(ratio,[.025,.975]).tolist(),file_bytes=m['file_bytes'],size_pct=m['file_bytes']/metrics['BF16']['file_bytes']*100,peak_rss_mib=m['peak_rss_mib'],peak_gpu_mib=m.get('peak_gpu_mib',0),prompt_tps=float(np.median([x['prompt_tps'] for x in bench])),generation_tps=float(np.median([x['generation_tps'] for x in bench])),discordant_items=int((y!=ref).sum()),evaluation_seconds=m['evaluation_seconds'])
 summary.append(row)
q4=summary[2]; q2=summary[4]
lo,hi=q4['delta_ci']; v4='PROVEN' if lo>=-2 else 'DISPROVEN' if hi < -2 else 'INCONCLUSIVE'
lo,hi=q2['delta_ci']; v2='PROVEN' if hi < -5 else 'DISPROVEN' if lo>=-5 else 'INCONCLUSIVE'
size=25<=q4['size_pct']<=40
verdict='DISPROVEN' if 'DISPROVEN' in [v4,v2] or not size else 'PROVEN' if v4==v2=='PROVEN' else 'INCONCLUSIVE'
report=dict(summary=summary,q4_accuracy_verdict=v4,q4_size_pass=size,q2_verdict=v2,verdict=verdict,bootstrap_seed=122,bootstrap_resamples=20000)
(ROOT/'results/summary.json').write_text(json.dumps(report,indent=2))
with (ROOT/'results/summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=summary[0].keys()); w.writeheader(); w.writerows(summary)
headline=f"4-bit kept {q4['retained_accuracy_pct']:.1f}% of the accuracy at {q4['size_pct']:.1f}% of the size."
lines=['# Quantization: five formats, one model','',f'**{headline}**','',f'Overall preregistered verdict: **{verdict}**. Q4 accuracy: {v4}; Q4 size: {"passes" if size else "fails"}; Q2 degradation: {v2}.','', '| Format | Correct /150 | Accuracy % | Δ vs BF16, pp (95% paired CI) | File MB | Size % | Peak host RSS MiB | Peak GPU MiB | Prompt tok/s | Generation tok/s |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in summary:
 lo,hi=r['delta_ci']
 lines.append(f"| {r['format']} | {r['correct']} | {r['accuracy_pct']:.2f} | {r['delta_pp']:+.2f} [{lo:+.2f}, {hi:+.2f}] | {r['file_bytes']/1e6:.2f} | {r['size_pct']:.2f} | {r['peak_rss_mib']:.1f} | {r['peak_gpu_mib']:.1f} | {r['prompt_tps']:.2f} | {r['generation_tps']:.2f} |")
lines += ['',f"Q4 accuracy retention 95% paired bootstrap CI: [{q4['retention_ci'][0]:.1f}%, {q4['retention_ci'][1]:.1f}%]. Retention is the ratio of observed test accuracies, not a fraction of capabilities preserved.", '', '## Plain-English takeaway', f"On these 150 science questions, the 4-bit model answered {q4['correct']} correctly versus {summary[0]['correct']} for the 16-bit model, using {q4['size_pct']:.1f}% as much disk space. BF16 strongly favored letter A, so the apparent accuracy gain is specific to this constrained test and does not establish that 4-bit is generally smarter.", '', '## Measurement details and limits', 'Public ARC-Easy test sample, four-choice filter, NumPy seed 122; identical zero-shot non-thinking chat prompts for all formats. The selected answer has the largest raw next-token logit among the single-token letters A/B/C/D. BF16 is the available 16-bit baseline, rather than F16. Each item begins with a reset KV cache; all prompts and four logits are saved. No model tuning or prompt selection used measured accuracy.', '', 'llama-cpp-python 0.3.36 CUDA 12.4 wheel; NVIDIA L4, all model layers offloaded, two CPU threads, context 1024, batch 512, microbatch 128, 99 requested GPU layers (full offload), flash attention off, mmap on. Peak RSS is the fresh evaluator process high-water mark through evaluation and benchmarking, including file-backed model pages and Python/runtime overhead. GPU memory is the peak process allocation sampled through NVML every 50 ms, including the CUDA context; brief peaks may be missed. Native logits are fetched before stopping each timer to synchronize GPU work. Throughput is the median of three warm measurements after one warmup: 256 prompt tokens and 64 greedy generation evaluations, counting each token evaluation, ignoring EOS. It excludes tokenization and loading. These are descriptive timing measurements without inferential CIs; generation benchmark uses a common synthetic science prompt, not accuracy answers.', '', 'Accuracy differences and retention CIs use 20,000 paired item bootstrap resamples, seed 122, percentile 95% intervals. No multiple-comparison correction; hypotheses concern Q4 and Q2, other formats are descriptive. Sampling uncertainty does not capture prompt sensitivity, training-data contamination, dataset choice, or systematic model biases. Quantized GGUFs include higher-precision tensors, so format names do not imply all weights have that bit width. Their metadata records Unsloth importance-matrix calibration (688 chunks); this experiment compares those prebuilt artifacts and cannot isolate nominal bit width from the quantizer/calibration recipe.', '', 'BF16 predicted A on 122/150 items; Q8 on 118, Q4 on 103, Q3 on 85, and Q2 on 149. The gold answer was A on 39/150 items. This strong letter bias and the low BF16 score limit interpretation: the >100% headline is an observed accuracy ratio under this forced-letter protocol, not evidence of general improvement. We preserved the preregistered prompt and scoring rather than tuning against these results. The Q4 rule is one-sided noninferiority (no loss greater than 2 pp), so a gain passes it.', '', '## Reproduce', 'Install the build dependencies listed in scripts/setup_runtime.sh, then run `python scripts/prepare.py`. For the measured GPU configuration, use scripts/remote_worker.py in a Colab L4 runtime with the frozen results/items.json copied in; it installs the pinned CUDA wheel and downloads models. On the measured Colab image this first attempt failed before inference because CUDA 12 shared libraries were absent; then execute scripts/remote_repair.py through `colab exec`. That script installs nvidia-cuda-runtime-cu12 and nvidia-cublas-cu12, supplies their library directories in LD_LIBRARY_PATH, and runs all five formats in fresh processes. These two compatibility packages were not version-pinned; the model files and llama-cpp-python wheel version were pinned. For CPU reproduction use `scripts/run_all.sh`; after downloading GPU results, run `python scripts/analyze.py`. Existing prediction rows are skipped; each format runs in its own process. Model downloads are pinned and SHA-256 verified. The CPU pilot took 79.105 seconds for one 77-token BF16 prompt, projecting to 197.8 minutes for BF16 alone, so the planned L4 fallback was used for all final measurements. Colab cost and shutdown evidence are in README.md and results/colab_usage_*.txt. The CPU pilot is preserved separately and excluded from the final paired comparison.', '', '## Sources', '- [Pinned public GGUF files](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/tree/50968a4468ef4233ed78cd7c3de230dd1d61a56b)', '- [ARC-Easy public dataset](https://huggingface.co/datasets/allenai/ai2_arc)', '- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)']
(ROOT/'writeup.md').write_text('\n'.join(lines)+'\n')
fig,axs=plt.subplots(1,3,figsize=(14,4.5),layout='constrained'); colors=['#52677d','#739eb0','#16876d','#d19a44','#c75b54']
x=np.arange(5)
axs[0].bar(x,[r['file_bytes']/1e6 for r in summary],color=colors); axs[0].set_ylabel('GGUF file size (decimal MB)')
d=np.array([r['delta_pp'] for r in summary]); ci=np.array([r['delta_ci'] for r in summary]); axs[1].errorbar(x,d,yerr=np.maximum(0,np.array([d-ci[:,0],ci[:,1]-d])),fmt='o',capsize=5,color='#16876d'); axs[1].axhline(0,color='gray',lw=1); axs[1].axhline(-2,color='#d19a44',ls='--',label='Q4 margin: −2 pp'); axs[1].axhline(-5,color='#c75b54',ls=':',label='Q2 threshold: −5 pp'); axs[1].set_ylabel('Accuracy difference vs BF16 (pp)\n95% paired bootstrap CI'); axs[1].legend(fontsize=8)
axs[2].bar(x-.18,[r['prompt_tps'] for r in summary],.36,label='Prompt',color='#52677d'); axs[2].bar(x+.18,[r['generation_tps'] for r in summary],.36,label='Generation',color='#16876d'); axs[2].set_ylabel('Tokens / second (NVIDIA L4)'); axs[2].legend()
for ax in axs: ax.set_xticks(x,formats,rotation=25); ax.spines[['top','right']].set_visible(False)
fig.suptitle('Qwen3-0.6B · 150 ARC-Easy questions · forced letter scoring\n'+headline+'\nBF16 chose A on 122/150 items; results are protocol-specific.',fontsize=12)
fig.savefig(ROOT/'chart.png',dpi=170)
print(json.dumps(report,indent=2)); print(headline)
