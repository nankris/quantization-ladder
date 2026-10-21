"""Local convenience monitor; remote GPU job is independent of this process."""
import subprocess,time,json,datetime,tarfile,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]; os.chdir(R); n=max([int(p.stem.rsplit('_',1)[1]) for p in (R/'results').glob('usage_monitor_*.txt')]+[0])
while True:
 n+=1
 try:
  rec=json.loads((R/'results/recovery.json').read_text())
  first=(datetime.datetime.fromisoformat(rec['first_session_absent_observed_utc'])-datetime.datetime.fromisoformat(rec['first_allocation_start_utc_approx'])).total_seconds()/3600*1.54
  current=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(rec['recovery_allocation_utc'])).total_seconds()/3600*1.54
  if first+current>=5.8:
   (R/'results/budget_stop.txt').write_text(subprocess.check_output(['colab','stop','-s','b10-122b'],text=True,timeout=50))
   raise SystemExit('Conservative CU limit reached')
  u=subprocess.check_output(['colab','usage'],text=True,timeout=50)
  (R/f'results/usage_monitor_{n:03d}.txt').write_text(u)
  subprocess.run(['colab','exec','-s','b10-122b','-f','scripts/poll.py','--timeout','25'],stdout=(R/'results/poll_latest.txt').open('w'),stderr=subprocess.STDOUT,timeout=55,check=True)
  subprocess.run(['colab','download','-s','b10-122b','/content/b10-122b/checkpoint.tar.gz','results/checkpoint.tar.gz'],stdout=subprocess.DEVNULL,timeout=55,check=True)
  with tarfile.open(R/'results/checkpoint.tar.gz') as tf: tf.extractall(R,filter='data')
  status=json.loads((R/'results/status.json').read_text()); counts={p.stem:sum(1 for _ in p.open()) for p in (R/'results').glob('confirm_*.jsonl')}
  print(datetime.datetime.now(datetime.timezone.utc).isoformat(),status,counts,flush=True)
  if status['status'] in ['complete','error']:
   (R/'results/stop.txt').write_text(subprocess.check_output(['colab','stop','-s','b10-122b'],text=True,timeout=50))
   (R/'results/usage_after.txt').write_text(subprocess.check_output(['colab','usage'],text=True,timeout=50))
   break
 except Exception as e: print(type(e).__name__,str(e),flush=True)
 time.sleep(45)
