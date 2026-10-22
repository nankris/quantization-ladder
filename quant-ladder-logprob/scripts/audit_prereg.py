"""Check that final reporting preserves the committed hypotheses and sample."""
import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def git(*args): return subprocess.check_output(['git','-C',str(R),*args])
first=git('show','e909540:README.md').decode()
current=(R/'README.md').read_text()
def section(s): return s.split('## Preregistered hypotheses and fixed decisions\n',1)[1].split('## Sample sizing',1)[0]
assert section(first)==section(current)
frozen=git('show','a8c729c:results/items.json')
assert frozen==(R/'results/items.json').read_bytes()
out={'status':'PASS','hypotheses_unchanged':True,'confirmatory_sample_unchanged':True,'sample_sha256':hashlib.sha256(frozen).hexdigest(),'preregistration_commit':git('show','-s','--format=%H %cI','e909540').decode().strip(),'sample_freeze_commit':git('show','-s','--format=%H %cI','a8c729c').decode().strip(),'sample_freeze_utc':json.loads((R/'results/power.json').read_text())['frozen_utc']}
(R/'results/preregistration_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
