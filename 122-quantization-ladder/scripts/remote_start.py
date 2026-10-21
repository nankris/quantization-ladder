from pathlib import Path
import tarfile,subprocess,os
ROOT=Path('/content/tig122'); ROOT.mkdir(exist_ok=True)
with tarfile.open('/content/tig122_upload.tar.gz') as tf: tf.extractall(ROOT,filter='data')
p=subprocess.Popen(['python',str(ROOT/'scripts/remote_worker.py')],stdout=open(ROOT/'worker.log','a'),stderr=subprocess.STDOUT,start_new_session=True)
print('Started worker',p.pid)
