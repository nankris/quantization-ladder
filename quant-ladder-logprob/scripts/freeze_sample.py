import json,math,datetime
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
def rows(f): return [json.loads(s) for s in (R/f'results/pilot_{f}.jsonl').read_text().splitlines()]
a=rows('BF16'); b=rows('Q4_K_M'); assert len(a)==len(b)==32
q=sum(x['correct']!=y['correct'] for x,y in zip(a,b))/32
planq=max(.02,q); needed=math.ceil((1.96+.842)**2*planq/.01**2)
pool=json.loads((R/'results/fresh_pool.json').read_text()); n=min(max(1000,needed),len(pool)); items=pool[:n]
(R/'results/items.json').write_text(json.dumps(items,indent=2))
power=float(__import__('statistics').NormalDist().cdf(.01*np.sqrt(n/planq)-1.96))
result=dict(pilot_n=32,pilot_discordance=q,planning_discordance=planq,needed_for_80_percent=needed,fresh_available=len(pool),confirmatory_n=n,approx_power_at_zero_difference=power,margin_for_80_percent_pp=(1.96+.842)*np.sqrt(planq/n)*100,frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(R/'results/power.json').write_text(json.dumps(result,indent=2))
with (R/'README.md').open('a') as f:
 f.write('\n## Sample freeze before confirmation\n\nThe disjoint 32-item pilot had BF16 28/32 and Q4 25/32 correct under cyclic scoring, with paired correctness discordance 3/32 = 0.09375. The registered calculation requests '+str(needed)+' items. Only '+str(len(pool))+' fresh deduplicated ARC-Easy items exist, so confirmation uses all '+str(n)+'. Approximate power at a true zero difference is '+f'{power*100:.1f}%'+', and the approximate 80%-power margin is '+f'{result["margin_for_80_percent_pp"]:.2f} pp'+'. The fixed 1 pp hypothesis and CI decisions remain unchanged. Pilot results are not confirmation and suggest the non-inferiority prediction may fail. Exact frozen records: results/items.json and results/power.json.\n')
print(json.dumps(result,indent=2))
