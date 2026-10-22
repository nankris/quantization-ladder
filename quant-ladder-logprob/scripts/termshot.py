#!/usr/bin/env python3
"""Render a text file as a terminal-window screenshot (PNG)."""
import argparse,re,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from matplotlib import font_manager
p=argparse.ArgumentParser(); p.add_argument('out'); p.add_argument('--title',required=True); p.add_argument('--file',required=True)
p.add_argument('--width',type=int,default=90); p.add_argument('--max',type=int,default=45); p.add_argument('--highlight',default='')
a=p.parse_args()
rows=[]
for line in Path(a.file).read_text().splitlines():
 rows.extend(textwrap.wrap(line,a.width,subsequent_indent='  ',replace_whitespace=False,drop_whitespace=False) or [''])
rows=rows[:a.max]
mono=ImageFont.truetype(font_manager.findfont('DejaVu Sans Mono'),18); sans=ImageFont.truetype(font_manager.findfont('DejaVu Sans Mono'),18)
cw=mono.getlength('M'); lh=26; top=42; pad=24
W=int(2*pad+cw*a.width+4); H=top+2*pad+lh*len(rows)
im=Image.new('RGB',(W,H),'#1b1d2a'); d=ImageDraw.Draw(im)
d.rectangle([0,0,W,top],fill='#2b2e3f')
for i,c in enumerate(['#ff5f57','#febc2e','#28c840']): d.ellipse([18+i*26,13,18+i*26+16,29],fill=c)
d.text((W/2,top/2),a.title,font=sans,fill='#b8bcd0',anchor='mm')
hl=re.compile(a.highlight) if a.highlight else None
for i,r in enumerate(rows):
 y=top+pad+lh*i
 hit=bool(hl and hl.search(r))
 if hit: d.rectangle([pad-6,y-3,W-pad+6,y+lh-4],fill='#4a3f27')
 d.text((pad,y),r,font=mono,fill='#ffd866' if hit else '#e8e8ee')
im.save(a.out,dpi=(150,150)); print('RENDERED',a.file,'->',a.out,im.size)
