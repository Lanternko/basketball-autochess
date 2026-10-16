import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'all-verification.json').exists();hashes={}
checks=['verification.json','fit-verification.json','context-verification.json','input-verification.json','probe-verification.json']
for f in [R/name for name in checks]+[Path('reports/player-impact-v40/all-verification.json'),Path('reports/player-impact-diagnostics/team-error-v39/all-verification.json')]:
 d=read(f);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p;hashes[p]=h
for j in read(R/'validation-manifest.json')['jobs']:assert sha(j['file'])==j['sha256'];hashes[j['file']]=j['sha256']
for p,h in read(R/'fit.json')['hashes'].items():assert sha(p)==h,p;hashes[p]=h
status=read(R/'status.json');assert not status['officialModelAdopted'] and not status['goalComplete'] and status['mainOvrHealthOnly'] and status['availabilityDisplayedSeparately'] and not status['injuryDeductionInMainOvr']
for p in R.iterdir():
 if p.is_file():hashes[str(p).replace('\\','/')]=sha(p)
out={'passed':True,'fullSeasonGames':28023,'diagnosticWorkloadGames':19200,'targetPlayers':582,'fullOvr':False,'officialModelAdopted':False,'goalComplete':False,'failedWinGateSeasons':status['failedWinGateSeasons'],'scope':'Closure of verified unadopted v41 experiment, preserved v40 prototype and team-error diagnostic. MainOVR health-only;availability separate per latest user. DisplayOVR and simulation may be separate models. Latest complete all-player ranking remains unaccepted v24.','hashes':hashes}
(R/'all-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('Frozen v41 closure;28023+19200 games;not adopted,no new fullOVR.')
