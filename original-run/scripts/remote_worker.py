from pathlib import Path
import subprocess,sys,os,json,time,traceback,tarfile
ROOT=Path('/content/quant-ladder'); os.chdir(ROOT)
started=time.time()
def run(cmd,log):
 with open(ROOT/'results'/log,'a') as f: subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
try:
 run([sys.executable,'-m','pip','install','-q','numpy','diskcache','jinja2','huggingface_hub','datasets','nvidia-ml-py'],'gpu_install.log')
 run([sys.executable,'-m','pip','install','llama-cpp-python==0.3.36','--only-binary=:all:','--no-deps','--index-url','https://abetlen.github.io/llama-cpp-python/whl/cu124'],'gpu_install.log')
 os.environ.update(HF_HUB_DISABLE_XET='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
 run([sys.executable,'scripts/prepare.py'],'gpu_prepare.log')
 import llama_cpp,platform
 (ROOT/'results/gpu_environment.json').write_text(json.dumps(dict(platform=platform.platform(),python=sys.version,system_info=llama_cpp.llama_print_system_info().decode()),indent=2))
 for fmt in ['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']:
  # Stop early rather than risk exceeding a 2 CU allocation at typical L4 rates.
  if time.time()-started>1000: raise RuntimeError('Remote 1000-second soft budget reached')
  run([sys.executable,'scripts/evaluate.py',fmt,'--gpu'],f'run_{fmt}.log')
 (ROOT/'results/remote_status.json').write_text(json.dumps(dict(status='complete',seconds=time.time()-started)))
except Exception:
 (ROOT/'results/remote_status.json').write_text(json.dumps(dict(status='error',traceback=traceback.format_exc(),seconds=time.time()-started)))
finally:
 with tarfile.open(ROOT/'results_bundle.tar.gz','w:gz') as tf: tf.add(ROOT/'results',arcname='results')
