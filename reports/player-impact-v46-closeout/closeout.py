"""Seal the accepted defense stage without modifying its frozen evidence."""
import hashlib,json
from pathlib import Path

root=Path('reports/player-impact-v46');out=Path('reports/player-impact-v46-closeout')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=read(root/'results-verification.json');d=read(root/'decision.json')
assert v['passed'] and d['adopted'] and v['matches']==28023
for key,name in [('reportSHA256','report.md'),('scoresSHA256','scores.json'),('fineScoresSHA256','fine-scores.json'),('decisionSHA256','decision.json')]:
 assert v[key]==sha(root/name),name
files=[root/f for f in ['report.md','decision.json','results-verification.json','protocol.json','candidate-run-protocol.json','candidate-run-verification.json','fit-verification.json','scores.json','fine-scores.json','make-fit.json','selection.json','seed-check.json','input.mjs','worker.mjs','run.mjs']]
files+=[Path('reports/player-impact-defense-current.json')]
result={'version':'v46','stage':'defense','status':'closed-accepted','scope':'Accepted measured NBA defense development baseline; not a claim that the whole system meets a global accuracy standard. Product preset and published OVR are unchanged.','verification':v,'evidenceSHA256':{p.as_posix():sha(p) for p in files},'nextVersion':'v47','nextTask':'Curry offense diagnosis using v46 unchanged; generic mechanisms only; report all-player/team and defense regressions.','remainingIssues':d['remainingWork'],'individualFineZoneCaution':d['targetSeasonWembanyama']['remainingIssue']}
(out/'status.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'closed':True,'version':'v46','filesSealed':len(files),'matches':v['matches']}))
