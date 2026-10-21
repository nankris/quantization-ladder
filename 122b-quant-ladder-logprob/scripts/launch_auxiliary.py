import subprocess
from pathlib import Path
R=Path('/content/b10-122b')
p=subprocess.Popen(['nohup','python',str(R/'scripts/auxiliary.py')],cwd=R,stdout=(R/'auxiliary.log').open('a'),stderr=subprocess.STDOUT,start_new_session=True); print('AUXILIARY_PID',p.pid)
