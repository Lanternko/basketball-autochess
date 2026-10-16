import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();old=read(R/'fit-protocol.json')
for p,h in old['hashes'].items():assert sha(p)==h,p
files=['scripts/run_isolated_report.py',str(R/'freeze-launcher.py').replace('\\','/'),str(R/'fit-protocol.json').replace('\\','/')]
out={'reason':'Direct launch failed before fitting because frozen select.py shadows standard-library select during multiprocessing import. Preserve all frozen sources and selection. Use runpy launcher that excludes report directory from Python module search; fitter explicitly imports v40 fitlib. No likelihood, data, fold, prior, solver or selection change.','hashes':{**old['hashes'],**{p:sha(p) for p in files}}};f=R/'launcher-protocol.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8')
