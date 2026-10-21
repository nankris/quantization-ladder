import tarfile,subprocess,os
from pathlib import Path
R=Path('/content/b10-122b'); R.mkdir(exist_ok=True)
with tarfile.open('/content/b10-122b-upload.tar.gz') as tf: tf.extractall(R)
p=subprocess.Popen(['nohup','python',str(R/'scripts/worker.py')],cwd=R,stdout=(R/'worker.log').open('a'),stderr=subprocess.STDOUT,start_new_session=True)
print('DETACHED_PID',p.pid)
