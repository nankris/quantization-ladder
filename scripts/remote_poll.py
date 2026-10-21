from pathlib import Path
import json
p=Path('/content/tig122/results')
for name in ['gpu_install.log','gpu_prepare.log','cuda_repair.log','run_BF16.log','run_Q8_0.log','run_Q4_K_M.log','run_Q3_K_M.log','run_Q2_K.log']:
 f=p/name
 if f.exists(): print(name, f.read_text()[-1200:])
for fmt in ['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']:
 f=p/f'predictions_{fmt}.jsonl'
 if f.exists(): print(fmt,len(f.read_text().splitlines()))
f=p/'remote_status.json'
if f.exists(): print('STATUS',f.read_text())
# Snapshot partial predictions as well as completed runs for safe retrieval.
import tarfile
with tarfile.open('/content/tig122/checkpoint.tar.gz','w:gz') as tf:
 tf.add(p,arcname='results')
