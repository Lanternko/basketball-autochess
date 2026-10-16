"""Publish the measured-development pointer only after independent verification."""
import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v47');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));v=read(R/'results-verification.json');d=read(R/'decision.json')
assert v['passed'] and d['adopted'] and all(d['gates'].values())
for key,file in [('reportSHA256','report.md'),('scoresSHA256','scores.json'),('fineScoresSHA256','fine-scores.json'),('decisionSHA256','decision.json')]:assert v[key]==hashlib.sha256((R/file).read_bytes()).hexdigest()
pointer={'version':'v47','scope':d['adoptionScope'],'defenseBaseline':'v46','sourceInput':(R/'input.mjs').as_posix(),'engine':(R/'engine.mjs').as_posix(),'creationPolicy':'rotation-space','run':'node reports/player-impact-v47/run.mjs','report':(R/'report.md').as_posix(),'decision':(R/'decision.json').as_posix(),'verification':(R/'results-verification.json').as_posix(),'gameDefaultChanged':False,'ovrRecomputed':False,'curryOffenseComplete':False}
Path('reports/player-impact-offense-current.json').write_text(json.dumps(pointer,indent=2),encoding='utf-8');print(json.dumps({'activated':'v47','defenseBaseline':'v46','productAndOVRChanged':False}))
