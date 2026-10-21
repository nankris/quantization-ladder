"""Collect final timing, cost estimate and run excerpts after successful shutdown."""
import datetime,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=R/'results'
assert json.loads((D/'status.json').read_text())['status']=='complete'
assert 'Session terminated' in (D/'stop.txt').read_text()
dt=datetime.datetime.fromisoformat
now=datetime.datetime.now(datetime.timezone.utc)
stop=datetime.datetime.fromtimestamp((D/'stop.txt').stat().st_mtime,datetime.timezone.utc)
recovery=json.loads((D/'recovery.json').read_text())
allocated=dt(recovery['recovery_allocation_utc'])
first_start=dt(recovery['first_allocation_start_utc_approx'])
first_absent=dt(recovery['first_session_absent_observed_utc'])
first_upper=(first_absent-first_start).total_seconds()/3600*1.54
second=(stop-allocated).total_seconds()/3600*1.54
before=float(re.search(r'balance: ([\d.]+)',(D/'usage_before.txt').read_text()).group(1))
after=float(re.search(r'balance: ([\d.]+)',(D/'usage_after.txt').read_text()).group(1))
cost={'GPU':'NVIDIA L4','allocation_start_utc_approx':first_start.isoformat(),'recovery_allocation_utc':allocated.isoformat(),'stopped_utc':stop.isoformat(),'isolated_rate_CU_per_hour':1.54,'first_allocation_CU_upper_bound':first_upper,'recovery_CU_estimate':second,'session_cu_estimate':first_upper+second,'session_cu_estimate_uncertainty':1.54/60,'account_balance_before':before,'account_balance_after':after,'account_balance_delta':before-after,'note':'Conservative duration-based upper estimate across two allocations. First VM release time unknown, charged through absent-session observation. Account balance delta can include unrelated concurrent work. Allocation timestamps have roughly one minute uncertainty.'}
(D/'cost.json').write_text(json.dumps(cost,indent=2))
timing=json.loads((D/'timing.json').read_text()); start=dt(timing['start_ist']); frozen=dt(json.loads((D/'power.json').read_text())['frozen_utc'])
clock=json.loads((D/'remote_clock.json').read_text())
gpu_end=max(dt(v) for k,v in clock['file_mtimes_utc'].items() if k.startswith('confirm_'))
analysis=json.loads((D/'analysis_stage.json').read_text()); analysis_start=dt(analysis['start_utc']); analysis_end=dt(analysis['end_utc'])
mins=lambda a,b:(b-a).total_seconds()/60
timing.update(end_ist=now.astimezone(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat(),actual_minutes=mins(start,now),per_stage_minutes={'setup':mins(start,frozen),'GPU run':mins(frozen,gpu_end),'eval':mins(analysis_start,analysis_end),'writeup':mins(gpu_end,now)-mins(analysis_start,analysis_end)},stage_note='Elapsed wall-clock allocation: setup ends at sample freeze (includes pilot); GPU run ends at last format metadata and includes outage/recovery downtime; eval is local analysis; remaining wall time is publication/writeup. Publication preparation also overlapped GPU evaluation. These are elapsed stage buckets, not exclusive labor measurements.',confirmatory_gpu_end_utc=gpu_end.isoformat())
(D/'timing.json').write_text(json.dumps(timing,indent=2))
parts=['122b run evidence: NVIDIA L4, two allocations under b10-122b after VM loss; no generated tokens.\n', '=== initial nvidia-smi ===\n'+(D/'nvidia-smi.txt').read_text(),'=== active GPU snapshot ===\n'+(D/'nvidia-smi-during.txt').read_text(),'=== first allocation evidence ===\n'+(D/'allocation1/nvidia-smi.txt').read_text(),'=== hash verification ===\n'+(D/'prepare.log').read_text()[-500:]]
for fmt in ['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']:
 p=D/f'confirm_{fmt}.log'
 parts+=['=== '+fmt+' ===\n'+(p.read_text() if p.exists() else (D/f'aux_{fmt}.log').read_text())[-700:],'=== metadata seconds (resumed formats report suffix work only) ===\n'+str(json.loads((D/f'confirm_{fmt}_meta.json').read_text())['seconds'])+'\n']
parts+=['=== completed status ===\n'+(D/'status.json').read_text(),'=== shutdown ===\n'+(D/'stop.txt').read_text(),'=== final usage ===\n'+(D/'usage_after.txt').read_text(),'=== cost accounting ===\n'+json.dumps(cost,indent=2),'=== timing ===\n'+json.dumps(timing,indent=2)]
(R/'figures/colab_run.txt').write_text('\n'.join(parts))
print(json.dumps({'timing':timing,'cost':cost},indent=2))
