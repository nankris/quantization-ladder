"""Second serial queue on the SAME VM/GPU; per-format locks prevent duplicates."""
import os,sys,site,glob,subprocess,json,time,traceback
from pathlib import Path
R=Path('/content/quant-ladder-logprob'); os.chdir(R); start=time.time()
libs=[p for s in site.getsitepackages() for p in glob.glob(s+'/nvidia/*/lib')]
env=dict(os.environ,LD_LIBRARY_PATH=':'.join(libs)+':'+os.environ.get('LD_LIBRARY_PATH',''),OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
try:
 for fmt in ['Q2_K','Q3_K_M','Q4_K_M']:
  if time.time()-start>10000: raise RuntimeError('Auxiliary watchdog')
  with (R/f'results/aux_{fmt}.log').open('a') as f: subprocess.run([sys.executable,'scripts/evaluate.py',fmt,'confirm'],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 (R/'results/aux_status.json').write_text(json.dumps(dict(status='complete',seconds=time.time()-start)))
except Exception:
 (R/'results/aux_status.json').write_text(json.dumps(dict(status='error',traceback=traceback.format_exc())))
