from pathlib import Path
import subprocess,tarfile,json,datetime
R=Path('/content/quant-ladder-logprob')
for name in ['results/status.json','worker.log']:
 p=R/name
 if p.exists(): print(name,p.read_text()[-2500:])
for p in sorted((R/'results').glob('*.log')): print(p.name,p.read_text()[-500:])
(R/'results/nvidia-smi-during.txt').write_text(subprocess.getoutput('nvidia-smi'))
print(subprocess.getoutput("ps -eo pid,etime,args | grep '[s]cripts/evaluate.py'"))
(R/'results/remote_clock.json').write_text(json.dumps(dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), file_mtimes_utc={p.name:datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat() for p in (R/'results').glob('*_meta.json')},status_mtime_utc=datetime.datetime.fromtimestamp((R/'results/status.json').stat().st_mtime,datetime.timezone.utc).isoformat()),indent=2))
with tarfile.open(R/'checkpoint.tar.gz','w:gz') as tf: tf.add(R/'results',arcname='results')
