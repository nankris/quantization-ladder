import sys,subprocess,os,time,json,site,glob,traceback,tarfile
from pathlib import Path
R=Path('/content/quant-ladder-logprob'); os.chdir(R); start=time.time()
def run(cmd,log='install.log',env=None):
 with (R/'results'/log).open('a') as f: subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
try:
 (R/'results/nvidia-smi.txt').write_bytes(subprocess.check_output(['nvidia-smi']))
 run([sys.executable,'-m','pip','install','-q','numpy','diskcache','jinja2','huggingface_hub','datasets','nvidia-cuda-runtime-cu12','nvidia-cublas-cu12'])
 run([sys.executable,'-m','pip','install','llama-cpp-python==0.3.36','--only-binary=:all:','--no-deps','--index-url','https://abetlen.github.io/llama-cpp-python/whl/cu124'])
 libs=[p for s in site.getsitepackages() for p in glob.glob(s+'/nvidia/*/lib')]
 env=dict(os.environ,LD_LIBRARY_PATH=':'.join(libs)+':'+os.environ.get('LD_LIBRARY_PATH',''),HF_HUB_DISABLE_XET='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
 run([sys.executable,'scripts/prepare.py'],'prepare.log',env)
 (R/'results/packages.txt').write_bytes(subprocess.check_output([sys.executable,'-m','pip','freeze']))
 for phase in ['pilot','confirm']:
  if phase=='confirm':
   (R/'results/status.json').write_text(json.dumps(dict(status='awaiting_preregistered_sample',seconds=time.time()-start)))
   while not (R/'results/items.json').exists():
    if time.time()-start>11500: raise RuntimeError('3.2 hour watchdog')
    time.sleep(5)
  for fmt in ['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']:
   if time.time()-start>11500: raise RuntimeError('3.2 hour watchdog')
   (R/'results/status.json').write_text(json.dumps(dict(status='running',phase=phase,format=fmt,seconds=time.time()-start)))
   run([sys.executable,'scripts/evaluate.py',fmt,phase],f'{phase}_{fmt}.log',env)
 (R/'results/status.json').write_text(json.dumps(dict(status='complete',seconds=time.time()-start)))
except Exception:
 (R/'results/status.json').write_text(json.dumps(dict(status='error',traceback=traceback.format_exc(),seconds=time.time()-start)))
finally:
 with tarfile.open(R/'bundle.tar.gz','w:gz') as tf: tf.add(R/'results',arcname='results')
