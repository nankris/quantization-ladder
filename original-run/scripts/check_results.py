"""Check saved predictions against the frozen items without model inference."""
import json, hashlib
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'results/items.json').read_text())
assert len(items)==150 and len({x['id'] for x in items})==150
reference=None
checks={}
for fmt in ['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']:
 rows=[json.loads(s) for s in (root/f'results/predictions_{fmt}.jsonl').read_text().splitlines()]
 assert len(rows)==150 and [r['id'] for r in rows]==[x['id'] for x in items]
 for row,item in zip(rows,items):
  assert row['gold']==item['gold']
  assert np.isfinite(row['letter_logits']).all()
  assert row['prediction']=='ABCD'[int(np.argmax(row['letter_logits']))]
  assert row['correct']==int(row['prediction']==row['gold'])
 prompts=[r['prompt'] for r in rows]
 if reference is None: reference=prompts
 assert prompts==reference
 m=json.loads((root/f'results/metrics_{fmt}.json').read_text())
 assert m['n']==150 and m['correct']==sum(r['correct'] for r in rows)
 assert m['gpu_info']['name']=='NVIDIA L4' and m['peak_gpu_mib']>0
 assert len(m['benchmark'])==4 and sum(not b['warmup'] for b in m['benchmark'])==3
 checks[fmt]={'items':150,'correct':m['correct'],'predictions_sha256':hashlib.sha256((root/f'results/predictions_{fmt}.jsonl').read_bytes()).hexdigest()}
(root/'results/validation.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
