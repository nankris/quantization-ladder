"""On replacement VM, fill the GPU and enforce a two-hour recovery deadline."""
import subprocess,sys,time,os,signal,json,datetime
from pathlib import Path
R=Path('/content/b10-122b')
if '--child' not in sys.argv:
 p=subprocess.Popen(['nohup',sys.executable,str(R/'scripts/recovery_control.py'),'--child'],stdout=(R/'recovery_control.log').open('a'),stderr=subprocess.STDOUT,start_new_session=True)
 print('RECOVERY_CONTROLLER_PID',p.pid)
else:
 allocated=datetime.datetime.fromisoformat(json.loads((R/'results/recovery.json').read_text())['recovery_allocation_utc']).timestamp()
 while (R/'results/packages.txt').stat().st_mtime<allocated:
  if time.time()-allocated>1200: raise RuntimeError('Runtime rebuild exceeded 20 minutes')
  time.sleep(5)
 aux=subprocess.Popen(['nohup',sys.executable,str(R/'scripts/auxiliary.py')],stdout=(R/'auxiliary.log').open('a'),stderr=subprocess.STDOUT,start_new_session=True)
 print('RECOVERY_AUX_PID',aux.pid,flush=True)
 while time.time()-allocated<7200:
  status=json.loads((R/'results/status.json').read_text())
  if status['status'] in ['complete','error']: break
  time.sleep(10)
 else:
  for pid in [8429,aux.pid]:
   try: os.killpg(pid,signal.SIGTERM)
   except ProcessLookupError: pass
  (R/'results/status.json').write_text(json.dumps({'status':'error','reason':'Two-hour replacement allocation budget deadline'}))
