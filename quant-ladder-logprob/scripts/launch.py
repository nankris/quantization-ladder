import tarfile,subprocess,os
from pathlib import Path
R=Path('/content/quant-ladder-logprob'); R.mkdir(exist_ok=True)
with tarfile.open('/content/quant-ladder-logprob-upload.tar.gz') as tf: tf.extractall(R)
p=subprocess.Popen(['nohup','python',str(R/'scripts/worker.py')],cwd=R,stdout=(R/'worker.log').open('a'),stderr=subprocess.STDOUT,start_new_session=True)
print('DETACHED_PID',p.pid)
