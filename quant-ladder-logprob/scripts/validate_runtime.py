import os,json,sys,site,glob,subprocess
from pathlib import Path
R=Path('/content/quant-ladder-logprob')
if '--child' not in sys.argv:
 libs=[p for s in site.getsitepackages() for p in glob.glob(s+'/nvidia/*/lib')]
 env=dict(os.environ,LD_LIBRARY_PATH=':'.join(libs)+':'+os.environ.get('LD_LIBRARY_PATH',''))
 subprocess.run([sys.executable,__file__,'--child'],env=env,check=True)
else:
 import numpy as np
 from llama_cpp import Llama
 x=json.loads((R/'results/pilot.json').read_text())[0]
 body='Answer the multiple-choice science question. Reply with only the letter A, B, C, or D.\n\n'+x['question']+'\n'+'\n'.join(f'{c}. {t}' for c,t in zip('ABCD',x['choices']))
 prompt='<|im_start|>user\n'+body+'<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'
 results={}; vecs=[]
 for all_logits in [False,True]:
  llm=Llama(model_path=str(R/'models/Qwen3-0.6B-BF16.gguf'),n_ctx=2048,n_batch=512,n_ubatch=128,n_gpu_layers=99,n_threads=2,logits_all=all_logits,verbose=False,flash_attn=False)
  ts=llm.tokenize(prompt.encode(),add_bos=False,special=True); llm.eval(ts)
  v=np.ctypeslib.as_array(llm._ctx.get_logits(),shape=(llm.n_vocab(),)).copy() if not all_logits else llm.scores[len(ts)-1].copy()
  lids=[llm.tokenize(c.encode(),add_bos=False)[0] for c in 'ABCD']; results[str(all_logits)]=v[lids].tolist(); vecs.append(v)
  if all_logits:
   next_id=lids[0]; llm.eval([next_id]); incremental=llm.scores[len(ts)].copy()
   llm.reset(); llm.eval(ts+[next_id]); full=llm.scores[len(ts)].copy()
   results['prefix_full_max_abs']=float(np.max(np.abs(incremental-full))); results['prefix_full_letters_max_abs']=float(np.max(np.abs(incremental[lids]-full[lids]))); results['prefix_full_argmax_same']=int(np.argmax(incremental))==int(np.argmax(full))
  llm.close(); del llm
 results['old_vs_new_max_abs']=float(np.max(np.abs(vecs[0]-vecs[1]))); results['old_vs_new_letters_max_abs']=float(np.max(np.abs(np.array(results['False'])-results['True'])))
 results['same_letter_argmax']=int(np.argmax(results['False']))==int(np.argmax(results['True']))
 results['pilot_id']=x['id']; (R/'results/runtime_validation.json').write_text(json.dumps(results,indent=2)); print(results)
