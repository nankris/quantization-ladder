import os,json,hashlib,time
from pathlib import Path
os.environ['HF_HUB_DISABLE_XET']='1'
from huggingface_hub import HfApi,hf_hub_download
from datasets import load_dataset
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
repo='unsloth/Qwen3-0.6B-GGUF'; rev='50968a4468ef4233ed78cd7c3de230dd1d61a56b'
manifest=ROOT/'results/manifest.json'
info=HfApi().model_info(repo,revision=rev,files_metadata=True)
files=[]
for fmt in ['BF16','Q8_0','Q4_K_M','Q3_K_M','Q2_K']:
 name=f'Qwen3-0.6B-{fmt}.gguf'
 item=next(x for x in info.siblings if x.rfilename==name)
 files.append(dict(format=fmt,file=name,bytes=item.size,lfs=dict(item.lfs) if item.lfs else None))
manifest.write_text(json.dumps(dict(repo=repo,revision=rev,files=files),indent=2))
if not (ROOT/'results/items.json').exists():
 ds=load_dataset('allenai/ai2_arc','ARC-Easy',split='test',revision='210d026faf9955653af8916fad021475a3f00453')
 eligible=[dict(x) for x in ds if len(x['choices']['text'])==4]
 idx=np.random.default_rng(122).choice(len(eligible),150,replace=False)
 items=[]
 for i in idx:
  x=eligible[int(i)]; labels=x['choices']['label']; gold='ABCD'[labels.index(x['answerKey'])]
  items.append(dict(id=x['id'],question=x['question'],choices=x['choices']['text'],gold=gold,source_index=int(i)))
 (ROOT/'results/items.json').write_text(json.dumps(items,indent=2))
 (ROOT/'results/data_provenance.json').write_text(json.dumps(dict(dataset='allenai/ai2_arc',config='ARC-Easy',split='test',fingerprint=ds._fingerprint,eligible=len(eligible),seed=122,dataset_revision='210d026faf9955653af8916fad021475a3f00453'),indent=2))
 print('Frozen 150 items',flush=True)
for x in files:
 print('Downloading',x['file'],flush=True)
 path=hf_hub_download(repo,x['file'],revision=rev,local_dir=ROOT/'models')
 digest=hashlib.sha256(Path(path).read_bytes()).hexdigest()
 assert digest==x['lfs']['sha256'],(x['file'],digest)
 x['verified_sha256']=digest
 manifest.write_text(json.dumps(dict(repo=repo,revision=rev,files=files),indent=2))
 print('Verified',x['format'],flush=True)
