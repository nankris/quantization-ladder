"""Render preserved files and computed results as real terminal screenshots."""
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=R/'results'; F=R/'figures/screenshots'; F.mkdir(exist_ok=True)
old=(D/'earlier_writeup.md').read_text()
(D/'screenshot_first.txt').write_text('\n'.join(old.splitlines()[:15])+'\n')
(D/'screenshot_flaw.txt').write_text(next(x for x in old.splitlines() if x.startswith('BF16 predicted A on'))+'\n')
s=json.loads((D/'summary.json').read_text())
lines=[f"Fresh confirmation: {s['n']} questions",'Format       Original %   Cyclic %    Text %']
for r in s['summary']:
 lines.append(f"{r['format']:<12} {r['unrotated_accuracy']:>9.2f} {r['cyclic_accuracy']:>10.2f} {r['text_accuracy']:>9.2f}")
(D/'screenshot_fixed.txt').write_text('\n'.join(lines)+'\n')
lines=[f"Overall verdict: {s['verdict']}",f"Q4 within 1 pp: {s['H1_Q4']}",f"Q2 drops >= 5 pp: {s['H2_Q2']}"]
for i in [2,4]:
 r=s['summary'][i]; lo,hi=r['cyclic_delta_ci']
 lines.append(f"{r['format']} - BF16: {r['cyclic_delta']:+.2f} pp; paired 95% CI [{lo:+.2f}, {hi:+.2f}]")
(D/'screenshot_verdict.txt').write_text('\n'.join(lines)+'\n')
for name,title,width in [('first','122: the original result',105),('flaw','122: the letter preference',90),('fixed','122b: fixed scoring on fresh questions',90),('verdict','122b: registered verdict',90)]:
 subprocess.run(['/workspace/tools/mlenv/bin/python','/workspace/work/tig/_batch10/vm/termshot.py',str(F/f'{name}.png'),'--title',title,'--file',str(D/f'screenshot_{name}.txt'),'--width',str(width),'--max','45','--highlight','Q4|BF16|verdict'],check=True)
 print((D/f'screenshot_{name}.txt').read_text())
