import subprocess
from pathlib import Path
R=Path('/content/quant-ladder-logprob')
p=subprocess.Popen(['nohup','python',str(R/'scripts/validate_runtime.py')],stdout=(R/'results/validation.log').open('a'),stderr=subprocess.STDOUT,start_new_session=True); print(p.pid)
