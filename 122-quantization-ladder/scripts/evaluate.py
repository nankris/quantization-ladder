"""Fresh process per format. Append+flush rows; resume by stable item IDs."""
import argparse,json,time,resource,os,platform,csv
from pathlib import Path
import numpy as np
from llama_cpp import Llama
import llama_cpp
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('format'); p.add_argument('--gpu',action='store_true'); p.add_argument('--limit',type=int,default=150); args=p.parse_args()
fmt=args.format
out=ROOT/f'results/predictions_{fmt}.jsonl'
meta_path=ROOT/f'results/metrics_{fmt}.json'
started=time.time()
gpu_layers=99 if args.gpu else 0
gpu_peak_mib=0.; gpu_info={}
if args.gpu:
 import pynvml,threading
 pynvml.nvmlInit(); gpu_handle=pynvml.nvmlDeviceGetHandleByIndex(0)
 gpu_info=dict(name=pynvml.nvmlDeviceGetName(gpu_handle),driver=pynvml.nvmlSystemGetDriverVersion(),total_mib=pynvml.nvmlDeviceGetMemoryInfo(gpu_handle).total/2**20)
 monitor_done=threading.Event()
 def monitor():
  global gpu_peak_mib
  while not monitor_done.is_set():
   for proc in pynvml.nvmlDeviceGetComputeRunningProcesses(gpu_handle):
    if proc.pid==os.getpid(): gpu_peak_mib=max(gpu_peak_mib,proc.usedGpuMemory/2**20)
   monitor_done.wait(.05)
 monitor_thread=threading.Thread(target=monitor,daemon=True); monitor_thread.start()

llm=Llama(model_path=str(ROOT/f'models/Qwen3-0.6B-{fmt}.gguf'),n_ctx=1024,n_batch=512,n_ubatch=128,n_threads=2,n_threads_batch=2,n_gpu_layers=gpu_layers,logits_all=False,verbose=False,seed=122,flash_attn=False)
letters='ABCD'; letter_ids=[llm.tokenize(s.encode(),add_bos=False) for s in letters]
assert all(len(x)==1 for x in letter_ids),letter_ids
letter_ids=[x[0] for x in letter_ids]
items=json.loads((ROOT/'results/items.json').read_text())
def next_logits():
 # v0.3.36 does not populate Python scores when logits_all=False.
 # The native context has one output row, the last decoded token.
 return np.ctypeslib.as_array(llm._ctx.get_logits(),shape=(llm.n_vocab(),))
def prompt(x):
 body='Answer the multiple-choice science question. Reply with only the letter A, B, C, or D.\n\n'+x['question']+'\n'+'\n'.join(f'{a}. {b}' for a,b in zip(letters,x['choices']))
 return '<|im_start|>user\n'+body+'<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'
# No item accuracy is used to tune this prompt. Exact strings saved with rows.
rows=[json.loads(s) for s in out.read_text().splitlines()] if out.exists() else []
done={x['id'] for x in rows}
with out.open('a',buffering=1) as f:
 for i,x in enumerate(items[:args.limit]):
  if x['id'] in done: continue
  text=prompt(x); tokens=llm.tokenize(text.encode(),add_bos=False,special=True)
  assert len(tokens)<1024
  llm.reset(); t=time.perf_counter(); llm.eval(tokens); last_logits=next_logits(); elapsed=time.perf_counter()-t
  logits=last_logits[letter_ids].astype(float).tolist()
  assert np.isfinite(logits).all(),logits
  pred=letters[int(np.argmax(logits))]
  row=dict(id=x['id'],index=i,gold=x['gold'],prediction=pred,correct=int(pred==x['gold']),letter_logits=logits,prompt_tokens=len(tokens),seconds=elapsed,prompt=text)
  f.write(json.dumps(row)+'\n'); f.flush(); os.fsync(f.fileno()); rows.append(row)
  if (i+1)%5==0: print(fmt,i+1,'items',round(time.time()-started,2),'seconds',flush=True)
metrics=json.loads(meta_path.read_text()) if meta_path.exists() else {}
# Benchmark once after full eval; first pass warmup, three measured repetitions.
if args.limit==150 and 'benchmark' not in metrics:
 bench_text=('The science museum explains energy, plants, water, rocks, and the solar system. '*100).encode()
 bench_tokens=llm.tokenize(bench_text,add_bos=False)[:256]
 benchmark=[]
 for rep in range(4):
  llm.reset(); t=time.perf_counter(); llm.eval(bench_tokens); next_logits(); pp=time.perf_counter()-t
  t=time.perf_counter()
  for _ in range(64):
   next_id=int(np.argmax(next_logits())); llm.eval([next_id])
  next_logits(); gen=time.perf_counter()-t
  benchmark.append(dict(rep=rep,warmup=rep==0,prompt_tokens=256,prompt_seconds=pp,prompt_tps=256/pp,generated_tokens=64,generation_seconds=gen,generation_tps=64/gen))
 metrics['benchmark']=benchmark
metrics.update(format=fmt,file_bytes=(ROOT/f'models/Qwen3-0.6B-{fmt}.gguf').stat().st_size,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,n=len(rows),correct=sum(x['correct'] for x in rows),evaluation_seconds=sum(x['seconds'] for x in rows),llama_cpp_python=llama_cpp.__version__,model_metadata=llm.metadata,platform=platform.platform(),threads=2,n_ctx=1024,n_batch=512,n_ubatch=128,n_gpu_layers=gpu_layers,peak_gpu_mib=gpu_peak_mib,gpu_info=gpu_info,flash_attn=False,letter_ids=letter_ids)
if args.gpu:
 monitor_done.set(); monitor_thread.join(); metrics['peak_gpu_mib']=gpu_peak_mib
meta_path.write_text(json.dumps(metrics,indent=2))
print(json.dumps(metrics),flush=True)
