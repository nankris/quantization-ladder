import json,hashlib,os
from pathlib import Path
import numpy as np
from datasets import load_dataset
from huggingface_hub import hf_hub_download
R=Path(__file__).resolve().parents[1]; os.environ['HF_HUB_DISABLE_XET']='1'
old=json.loads((R/'results/earlier_items.json').read_text()); ids={x['id'] for x in old}; texts={x['question'].strip() for x in old}
rev='210d026faf9955653af8916fad021475a3f00453'
pool=[]; seen=set(ids); seenq=set(texts)
for split in ['train','validation','test']:
 ds=load_dataset('allenai/ai2_arc','ARC-Easy',split=split,revision=rev)
 for x in ds:
  if len(x['choices']['text'])!=4 or x['id'] in seen or x['question'].strip() in seenq: continue
  seen.add(x['id']); seenq.add(x['question'].strip())
  pool.append(dict(id=x['id'],question=x['question'],choices=x['choices']['text'],gold='ABCD'[x['choices']['label'].index(x['answerKey'])],split=split))
train=[x for x in pool if x['split']=='train']; rng=np.random.default_rng(122032)
pilot=[train[int(i)] for i in rng.choice(len(train),32,replace=False)]; pi={x['id'] for x in pilot}
fresh=[x for x in pool if x['id'] not in pi]; rng=np.random.default_rng(1222026); rng.shuffle(fresh)
for name,items in [('pilot',pilot),('fresh_pool',fresh)]:
 p=R/f'results/{name}.json'
 if p.exists(): assert json.loads(p.read_text())==items
 else: p.write_text(json.dumps(items,indent=2))
(R/'results/provenance.json').write_text(json.dumps(dict(dataset='allenai/ai2_arc',revision=rev,pilot_n=len(pilot),fresh_available=len(fresh),excluded_earlier=len(ids)),indent=2))
m=json.loads((R/'results/manifest.json').read_text())
for x in m['files']:
 p=hf_hub_download(m['repo'],x['file'],revision=m['revision'],local_dir=R/'models')
 with open(p,'rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
 assert digest==x['verified_sha256']; print('verified',x['format'],flush=True)
