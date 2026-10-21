import os,json,time,argparse,hashlib
from pathlib import Path
import numpy as np
from llama_cpp import Llama
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('fmt'); p.add_argument('phase',choices=['pilot','confirm']); a=p.parse_args()
# Serialize writers for each phase/format when two scheduling workers meet.
import fcntl
lock=(R/f'results/{a.phase}_{a.fmt}.lock').open('w')
fcntl.flock(lock,fcntl.LOCK_EX)
meta_existing=R/f'results/{a.phase}_{a.fmt}_meta.json'
output_existing=R/f'results/{a.phase}_{a.fmt}.jsonl'
items_existing=R/f'results/{"pilot" if a.phase=="pilot" else "items"}.json'
if meta_existing.exists() and output_existing.exists():
 expected=json.loads(items_existing.read_text())
 completed=[json.loads(s) for s in output_existing.read_text().splitlines()]
 if [x['id'] for x in expected]==[x['id'] for x in completed]:
  print('Already complete:',a.phase,a.fmt,len(completed),flush=True)
  raise SystemExit(0)
llm=Llama(model_path=str(R/f'models/Qwen3-0.6B-{a.fmt}.gguf'),n_ctx=2048,n_batch=512,n_ubatch=128,n_threads=2,n_threads_batch=2,n_gpu_layers=99,logits_all=True,verbose=False,seed=122,flash_attn=False)
L='ABCD'; lids=[llm.tokenize(c.encode(),add_bos=False)[0] for c in L]; assert all(len(llm.tokenize(c.encode(),add_bos=False))==1 for c in L)
def prompt(x,order,text=False):
 instruction='Answer the multiple-choice science question. Reply with only the '+('exact answer text.' if text else 'letter A, B, C, or D.')
 body=instruction+'\n\n'+x['question']+'\n'+'\n'.join(f'{c}. {x["choices"][j]}' for c,j in zip(L,order))
 return '<|im_start|>user\n'+body+'<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'
def tok(s): return llm.tokenize(s.encode(),add_bos=False,special=True)
def logp(v):
 v=np.asarray(v,dtype=np.float64); return v-(v.max()+np.log(np.exp(v-v.max()).sum()))
items=json.loads((R/f'results/{"pilot" if a.phase=="pilot" else "items"}.json').read_text())
out=R/f'results/{a.phase}_{a.fmt}.jsonl'
# Drop only incomplete trailing rows following a VM crash.
if out.exists():
 good=[]
 for line in out.read_text().splitlines():
  try: good.append(json.loads(line))
  except json.JSONDecodeError: break
 out.write_text(''.join(json.dumps(x)+'\n' for x in good))
else: good=[]
done={x['id'] for x in good}; start=time.time()
with out.open('a',buffering=1) as f:
 for i,x in enumerate(items):
  if x['id'] in done: continue
  rotations=[]; aligned=[]; input_tokens=0; target_tokens=0
  for shift in range(4):
   order=[(j+shift)%4 for j in range(4)]; ts=tok(prompt(x,order)); llm.reset(); llm.eval(ts)
   # logits_all=True fills Python scores, native final output is independently checked.
   v=llm.scores[len(ts)-1].copy()
   native=np.ctypeslib.as_array(llm._ctx.get_logits_ith(len(ts)-1),shape=(llm.n_vocab(),)).copy()
   assert np.allclose(v,native,atol=1e-5)
   lp=logp(v)[lids]; mapped=[0.]*4
   for pos,j in enumerate(order): mapped[j]=float(lp[pos])
   aligned.append(mapped); rotations.append(dict(order=order,letter_logprobs=lp.tolist(),prediction=L[int(np.argmax(lp))],prompt_tokens=len(ts)))
   input_tokens+=len(ts); target_tokens+=4
  base=tok(prompt(x,list(range(4)),True)); text_scores=[]; text_token_logs=[]; text_token_ids=[]
  for option in x['choices']:
   target=llm.tokenize(option.encode(),add_bos=False); assert target
   full=base+target; assert len(full)<2048
   llm.reset(); llm.eval(full)
   logs=[float(logp(llm.scores[len(base)-1+j])[t]) for j,t in enumerate(target)]
   text_scores.append(float(np.mean(logs))); text_token_logs.append(logs); text_token_ids.append(target)
   input_tokens+=len(base); target_tokens+=len(target)
  pred=L[int(np.argmax(np.mean(aligned,axis=0)))]; tp=L[int(np.argmax(text_scores))]
  row=dict(id=x['id'],index=i,gold=x['gold'],prediction=pred,correct=int(pred==x['gold']),unrotated=rotations[0]['prediction'],text_prediction=tp,text_correct=int(tp==x['gold']),rotations=rotations,aligned_mean_logprobs=np.mean(aligned,axis=0).tolist(),text_mean_logprobs=text_scores,text_token_logprobs=text_token_logs,text_token_ids=text_token_ids,prompt_tokens=input_tokens,scored_candidate_tokens=target_tokens,generated_tokens=0)
  f.write(json.dumps(row)+'\n'); f.flush()
  if (i+1)%25==0 or a.phase=='pilot': os.fsync(f.fileno()); print(a.phase,a.fmt,i+1,'seconds',round(time.time()-start,2),flush=True)
(R/f'results/{a.phase}_{a.fmt}_meta.json').write_text(json.dumps(dict(seconds=time.time()-start,model_metadata=llm.metadata,letter_token_ids=lids,n=len(items)),indent=2))
