import json,re
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'results/summary.json').read_text())
assert s['n']==4972
required=['README.md','writeup.md','blog.md','results/timing.json','results/cost.json','results/summary.csv','figures/accuracy.png','figures/deltas.png','figures/letter_distribution.png','figures/table.png','figures/diagram.png','figures/diagram.excalidraw','figures/colab_run.txt','results/stop.txt']
for name in required: assert (R/name).stat().st_size>0,name
blog=(R/'blog.md').read_text(); words=len(re.findall(r"\b[\w'-]+\b",blog)); assert 1200<=words<=1700,words; assert '\u2014' not in blog
for quote in ['126.7%','33.1%','40.00%','50.67%','25.33%','122/150','39/150']: assert quote in blog,quote
for p in (R/'figures').glob('*.png'):
 im=Image.open(p); assert im.width>=900 and im.height>=450,(p,im.size)
 if p.name not in ['diagram.png']: assert 149<=im.info['dpi'][0]<=151,(p,im.info)
diagram=json.loads((R/'figures/diagram.excalidraw').read_text()); assert diagram['type']=='excalidraw'; assert all(16<=x['fontSize']<=20 for x in diagram['elements'] if x['type']=='text')
t=json.loads((R/'results/timing.json').read_text()); assert all(k in t for k in ['estimated_minutes','actual_minutes','start_ist','end_ist','per_stage_minutes','GPU'])
c=json.loads((R/'results/cost.json').read_text()); assert c['session_cu_estimate']<6
proof=(R/'figures/colab_run.txt').read_text(); assert 'NVIDIA L4' in proof and 'seconds' in proof
assert 'Session terminated' in (R/'results/stop.txt').read_text()

assert len(list((R/'figures/screenshots').glob('*.png')))>=4
for name in ['first','flaw','fixed','verdict']: assert f'figures/screenshots/{name}.png' in blog

print(json.dumps(dict(status='PASS',n=s['n'],verdict=s['verdict'],blog_words=words,figures='150 dpi charts plus rendered diagram',CU_estimate=c['session_cu_estimate']),indent=2))
