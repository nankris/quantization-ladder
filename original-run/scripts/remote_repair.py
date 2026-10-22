from pathlib import Path
import subprocess,sys,os
root=Path('/content/quant-ladder')
# Install compatibility libraries in a child process, then launch with their search path.
code=r'''
import subprocess,sys,os,site,glob,json,time,tarfile,traceback
from pathlib import Path
root=Path('/content/quant-ladder'); os.chdir(root)
started=time.time()
try:
 with open(root/'results/cuda_repair.log','a') as f:
  subprocess.run([sys.executable,'-m','pip','install','-q','nvidia-cuda-runtime-cu12','nvidia-cublas-cu12'],stdout=f,stderr=subprocess.STDOUT,check=True)
 libdirs=[p for s in site.getsitepackages() for p in glob.glob(s+'/nvidia/*/lib')]
 env=dict(os.environ,LD_LIBRARY_PATH=':'.join(libdirs)+':'+os.environ.get('LD_LIBRARY_PATH',''),OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
 info="import llama_cpp,platform,json,sys; print(json.dumps(dict(platform=platform.platform(),python=sys.version,system_info=llama_cpp.llama_print_system_info().decode()),indent=2))"
 (root/'results/gpu_environment.json').write_bytes(subprocess.check_output([sys.executable,'-c',info],env=env))
 for fmt in ['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']:
  if time.time()-started>900: raise RuntimeError('Repair soft budget reached')
  with open(root/f'results/run_{fmt}.log','a') as f:
   subprocess.run([sys.executable,'scripts/evaluate.py',fmt,'--gpu'],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 (root/'results/remote_status.json').write_text(json.dumps(dict(status='complete',seconds=time.time()-started)))
except Exception:
 (root/'results/remote_status.json').write_text(json.dumps(dict(status='error',traceback=traceback.format_exc(),seconds=time.time()-started)))
finally:
 with tarfile.open(root/'results_bundle.tar.gz','w:gz') as tf: tf.add(root/'results',arcname='results')
'''
(root/'scripts/repair_worker.py').write_text(code)
p=subprocess.Popen([sys.executable,str(root/'scripts/repair_worker.py')],stdout=open(root/'repair.log','a'),stderr=subprocess.STDOUT,start_new_session=True)
print('Started repair worker',p.pid)
