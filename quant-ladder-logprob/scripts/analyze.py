import json,csv,collections,datetime
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]; F=R/'figures'; F.mkdir(exist_ok=True)
analysis_start=datetime.datetime.now(datetime.timezone.utc)
formats=['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']; labels=['BF16','Q8','Q4','Q3','Q2']
items=json.loads((R/'results/items.json').read_text()); n=len(items); ids=[x['id'] for x in items]
rows={f:[json.loads(s) for s in (R/f'results/confirm_{f}.jsonl').read_text().splitlines()] for f in formats}
import hashlib
for fmt,check in json.loads((R/'results/recovery_prefix_checksums.json').read_text()).items():
 prefix=rows[fmt][:check['retained_rows']]
 assert hashlib.sha256(json.dumps(prefix,sort_keys=True,separators=(',',':')).encode()).hexdigest()==check['canonical_sha256'],fmt
for f,rs in rows.items():
 assert [r['id'] for r in rs]==ids and len(rs)==n
 for x,r in zip(items,rs):
  assert x['gold']==r['gold']
  assert r['prediction']=='ABCD'[int(np.argmax(r['aligned_mean_logprobs']))]
  assert r['text_prediction']=='ABCD'[int(np.argmax(r['text_mean_logprobs']))]
  assert r['correct']==int(r['prediction']==r['gold'])
  assert r['text_correct']==int(r['text_prediction']==r['gold'])
  assert r['unrotated']==r['rotations'][0]['prediction']
  mapped=[]
  for shift,rotation in enumerate(r['rotations']):
   assert rotation['order']==[(j+shift)%4 for j in range(4)]
   assert rotation['prediction']=='ABCD'[int(np.argmax(rotation['letter_logprobs']))]
   values=np.empty(4)
   for pos,j in enumerate(rotation['order']): values[j]=rotation['letter_logprobs'][pos]
   mapped.append(values)
  assert np.allclose(np.mean(mapped,axis=0),r['aligned_mean_logprobs'],rtol=0,atol=1e-10)
  assert np.allclose([np.mean(v) for v in r['text_token_logprobs']],r['text_mean_logprobs'],rtol=0,atol=1e-10)

for f in formats[1:]:
 assert [r['prompt_tokens'] for r in rows[f]]==[r['prompt_tokens'] for r in rows['BF16']]
 assert [r['text_token_ids'] for r in rows[f]]==[r['text_token_ids'] for r in rows['BF16']]
old=json.loads((R/'results/earlier_items.json').read_text()); pilot=json.loads((R/'results/pilot.json').read_text())
assert not set(ids)&{x['id'] for x in old+pilot}
assert not {x['question'].strip() for x in items}&{x['question'].strip() for x in old+pilot}
rng=np.random.default_rng(1222026)
# Paired multinomial on joint outcomes is exactly an item bootstrap for binary differences.
def ci_diff(a,b):
 n=len(a); d=np.asarray(a,dtype=int)-np.asarray(b,dtype=int); v,c=np.unique(d,return_counts=True)
 boot=rng.multinomial(n,c/n,size=20000)@v/n*100
 return np.quantile(boot,[.025,.975]).tolist()
def ci_acc(a):
 n=len(a); return (np.quantile(rng.binomial(n,np.mean(a),20000)/n*100,[.025,.975])).tolist()
def correct(f,m):
 return np.array([r['correct'] if m=='cyclic' else r['text_correct'] if m=='text' else r['unrotated']==r['gold'] for r in rows[f]],dtype=int)
summary=[]
for f in formats:
 row={'format':f,'n':n}
 for m in ['cyclic','unrotated','text']:
  a=correct(f,m); b=correct('BF16',m)
  row[m+'_correct']=int(a.sum())
  row[m+'_paired_outcomes_vs_BF16']={'both_correct':int(((a==1)&(b==1)).sum()),'both_wrong':int(((a==0)&(b==0)).sum()),'format_only_correct':int(((a==1)&(b==0)).sum()),'BF16_only_correct':int(((a==0)&(b==1)).sum())}
  row[m+'_accuracy']=float(a.mean()*100); row[m+'_ci']=ci_acc(a); row[m+'_delta']=float((a-b).mean()*100); row[m+'_delta_ci']=ci_diff(a,b)
  if m!='unrotated':
   u=correct(f,'unrotated'); row[m+'_minus_unrotated_pp']=float((a-u).mean()*100); row[m+'_minus_unrotated_ci']=ci_diff(a,u)
 row['unrotated_counts']=dict(collections.Counter(r['unrotated'] for r in rows[f]))
 row['rotations_counts']=[dict(collections.Counter(r['rotations'][s]['prediction'] for r in rows[f])) for s in range(4)]
 row['rotation_accuracy']=[sum('ABCD'[r['rotations'][shift]['order']['ABCD'.index(r['rotations'][shift]['prediction'])]]==r['gold'] for r in rows[f])/n*100 for shift in range(4)]
 row['cyclic_identity_counts']=dict(collections.Counter(r['prediction'] for r in rows[f]))
 row['prompt_tokens']=sum(r['prompt_tokens'] for r in rows[f]); row['candidate_tokens']=sum(r['scored_candidate_tokens'] for r in rows[f]); row['generated_tokens']=0
 row['evaluated_input_tokens']=row['prompt_tokens']+row['candidate_tokens']-16*n
 summary.append(row)
q4=summary[2]['cyclic_delta_ci']; q2=summary[4]['cyclic_delta_ci']
v1='PROVEN' if q4[0]>=-1 else 'DISPROVEN' if q4[1]<-1 else 'INCONCLUSIVE'
v2='PROVEN' if q2[1]<=-5 else 'DISPROVEN' if q2[0]>-5 else 'INCONCLUSIVE'
overall='DISPROVEN' if 'DISPROVEN' in [v1,v2] else 'PROVEN' if v1==v2=='PROVEN' else 'INCONCLUSIVE'
result={'n':n,'summary':summary,'H1_Q4':v1,'H2_Q2':v2,'verdict':overall,'gold_counts':dict(collections.Counter(x['gold'] for x in items)),'split_counts':dict(collections.Counter(x['split'] for x in items)),'validation':'complete, paired IDs and scoring validated, no earlier/pilot IDs or exact questions'}
subgroups=[]
for split in ['train','validation','test']:
 mask=np.array([x['split']==split for x in items]); base=correct('BF16','cyclic')[mask]
 for f in formats:
  ac=correct(f,'cyclic')[mask]; subgroups.append(dict(split=split,format=f,n=len(ac),accuracy=float(ac.mean()*100),delta=float((ac-base).mean()*100),delta_ci=ci_diff(ac,base)))
(R/'results/descriptive_split_checks.json').write_text(json.dumps({'note':'Post hoc descriptive split sensitivity; not a registered hypothesis or selection rule','rows':subgroups},indent=2))
(R/'results/summary.json').write_text(json.dumps(result,indent=2))
(R/'results/token_counts.json').write_text(json.dumps({'note':'Per format. Prompt tokens include the repeated text-scoring prefixes; candidate counts include 16 letter scores per item from distributions, plus teacher-forced text tokens. Evaluated input tokens exclude letter candidates, which are scored but not fed. Generated tokens are zero. All counts come from the served model tokenizer.','formats':[{k:r[k] for k in ['format','n','prompt_tokens','candidate_tokens','evaluated_input_tokens','generated_tokens']} for r in summary]},indent=2))
with (R/'results/summary.csv').open('w') as f:
 keys=['format','n','cyclic_accuracy','cyclic_delta','cyclic_delta_ci','unrotated_accuracy','text_accuracy','unrotated_counts']; w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows({k:r[k] for k in keys} for r in summary)
with (R/'results/predicted_letters.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['format','view','A','B','C','D']); w.writeheader()
 for row in summary:
  for view,counts in [('original',row['unrotated_counts']),('balanced_original_identity',row['cyclic_identity_counts'])]+[(f'rotation_{j}',v) for j,v in enumerate(row['rotations_counts'])]:
   w.writerow(dict(format=row['format'],view=view,**{c:counts.get(c,0) for c in 'ABCD'}))
plt.rcParams.update({'font.size':12,'axes.titlesize':16,'axes.labelsize':12,'figure.dpi':150,'savefig.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
colors=['#345995','#e09f3e','#158477']
fig,ax=plt.subplots(figsize=(9,5)); x=np.arange(5)
for i,m in enumerate(['unrotated','cyclic','text']):
 vals=[r[m+'_accuracy'] for r in summary]; cis=np.array([r[m+'_ci'] for r in summary]).T
 ax.errorbar(x+(i-1)*.16,vals,yerr=[np.array(vals)-cis[0],cis[1]-np.array(vals)],fmt='o-',capsize=3,label={'unrotated':'Letters: original order','cyclic':'Letters: four rotations (primary)','text':'Full text: mean token logprob'}[m],color=colors[i])
ax.set(xticks=x,xticklabels=labels,ylabel='Accuracy (%)',xlabel='Weight format',title=f'The scoring rule changes the quantization story (n={n:,})'); ax.legend(fontsize=10); ax.grid(axis='y',alpha=.2); fig.tight_layout(); fig.savefig(F/'accuracy.png'); plt.close(fig)
fig,axes=plt.subplots(2,1,figsize=(9,6.5),gridspec_kw={'height_ratios':[2.2,1]})
for ax,subset,ys,title,limits in [
 (axes[0],summary[1:4],[2,1,0],'Q4 misses the one-point non-inferiority margin',(-7.5,.6)),
 (axes[1],summary[4:],[0],'Q2 degradation exceeds the five-point target',(-44,1))]:
 for y,r in zip(ys,subset):
  lo,hi=r['cyclic_delta_ci']; d=r['cyclic_delta']
  ax.errorbar(d,y,xerr=[[d-lo],[hi-d]],fmt='o',capsize=5,color='#345995',markersize=7)
 ax.axvline(0,color='grey',lw=1)
 ax.set(yticks=ys,yticklabels=[labels[formats.index(r['format'])] for r in subset],xlabel='Accuracy difference from BF16 (percentage points)',title=title,xlim=limits)
 ax.grid(axis='x',alpha=.2)
axes[0].axvline(-1,color='#158477',ls='--',label='Q4 tolerance: -1 pp'); axes[0].legend(loc='lower right',fontsize=10); axes[0].set_ylim(-.5,2.5)
axes[1].axvline(-5,color='#bd4b42',ls=':',label='Q2 target: -5 pp'); axes[1].legend(loc='upper right',fontsize=10); axes[1].set_ylim(-.6,.6)
fig.suptitle('Paired 95% intervals after cyclic balancing',fontsize=16)
fig.tight_layout(); fig.savefig(F/'deltas.png'); plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(10,4.8),sharey=True)
for ax,rot,title in [(axes[0],False,'Original order'),(axes[1],True,'All four rotations')]:
 bottom=np.zeros(5)
 for j,c in enumerate('ABCD'):
  vals=np.array([sum(count.get(c,0) for count in r['rotations_counts'])/(4*n)*100 if rot else r['unrotated_counts'].get(c,0)/n*100 for r in summary]); ax.bar(labels,vals,bottom=bottom,label=c,color=['#345995','#e09f3e','#158477','#9a77b5'][j]); bottom+=vals
 ax.set(title=title,xlabel='Weight format',ylim=(0,100))
axes[0].set_ylabel('Predicted output letter (%)'); axes[1].legend(title='Letter',bbox_to_anchor=(1.02,1)); fig.suptitle('Rotations reveal remaining position preferences'); fig.tight_layout(); fig.savefig(F/'letter_distribution.png'); plt.close(fig)
fig,ax=plt.subplots(figsize=(11,3.4)); ax.axis('off')
body=[]
for label,r in zip(labels,summary):
 d=r['cyclic_delta']; lo,hi=r['cyclic_delta_ci']; body.append([label,f'{r["unrotated_accuracy"]:.2f}',f'{r["cyclic_accuracy"]:.2f}',f'{d:+.2f} [{lo:+.2f}, {hi:+.2f}]',f'{r["text_accuracy"]:.2f}'])
t=ax.table(cellText=body,colLabels=['Format','Original %','Cyclic %','Δ vs BF16, pp [95% CI]','Text %'],loc='center',cellLoc='center',colWidths=[.10,.15,.15,.40,.15]); t.auto_set_font_size(False); t.set_fontsize(12); t.scale(1,1.8)
for (i,j),cell in t.get_celld().items():
 cell.set_edgecolor('#dddddd')
 if i==0: cell.set_facecolor('#345995'); cell.set_text_props(color='white',weight='bold')
 elif i%2: cell.set_facecolor('#eff3f7')
ax.set_title(f'Qwen3-0.6B on {n:,} fresh ARC-Easy questions',pad=12); fig.tight_layout(); fig.savefig(F/'table.png',bbox_inches='tight'); plt.close(fig)
(R/'results/analysis_stage.json').write_text(json.dumps({'start_utc':analysis_start.isoformat(),'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
print(json.dumps(result,indent=2))
