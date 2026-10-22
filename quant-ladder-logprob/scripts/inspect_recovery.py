from pathlib import Path
import subprocess,time
R=Path('/content/quant-ladder-logprob')
print(subprocess.getoutput("ps -eo pid,ppid,etime,args | grep -E '(8429|8922|pip install|scripts/prepare.py|scripts/evaluate.py)'"))
for name in ['results/install.log','results/prepare.log','recovery_control.log']:
 p=R/name
 print(name,'mtime',time.ctime(p.stat().st_mtime) if p.exists() else 'missing',p.read_text()[-600:] if p.exists() else '')
print(subprocess.getoutput('du -sh /content/quant-ladder-logprob/models /root/.cache/pip 2>/dev/null'))
