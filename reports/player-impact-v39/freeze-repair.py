import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
previous=read(R/'source-fit-protocol.json');hashes={**previous['hashes'],**{str(R/f).replace('\\','/'):sha(R/f) for f in ['fitlib_repair.py','fit_repair.py','freeze-repair.py','source-fit-protocol.json']}}
for p,h in hashes.items():assert sha(p)==h
out={'reason':'First run stopped because one fit gradient .0016126148631486759 exceeded frozen .001 tolerance. No selection file produced. Preserve57 accepted checkpoints and original frozen sources. Missing fits use identical objective and L-BFGS options followed by exact Hessian Newton refinement; tolerance not loosened. No hyperparameter, fold, dataset, selection criterion or runtime model change. New solver frozen before resuming. Independently verify all old and new fits.', 'retainedCheckpoints':{str(p).replace('\\','/'):sha(p) for p in sorted((R/'fits').glob('*.json'))},'hashes':hashes}
f=R/'solver-repair-protocol.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8');print('Solver repair frozen',len(out['retainedCheckpoints']))
