import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-diagnostics/pass-row-feasibility-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ['prototype-verification.json','source-prototype-verification.json','lp-verification.json','projection-verification.json']:
 d=read(R/name);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
a=read(R/'audit.json');p=read(R/'source-prototype-verification.json');assert len(a['seasons'])==len(p['seasons'])==4
for x,y in zip(a['seasons'],p['seasons']):
 assert x['season']==y['season']
 for before,after in [('sourceShotStates','shotStates'),('strictlyFeasibleShotStates','strictSourceStatesChecked'),('nonStrictShotStates','nonStrictSourceStatesRejected'),('unsupportedMakesInStrictlyFeasibleStates','legacyUnsupportedMakesWithPositiveOwnNow'),('unsupportedMakesNeedingSupplyAdjustment','legacyUnsupportedMakesStillPending')]:assert x[before]==y[after]
assert p['legacyUnsupportedMakesWithPositiveOwnNow']==850 and p['legacyUnsupportedMakesStillPending']==41
assert read(R/'prototype-verification.json')['mean70Players']==582 and read(R/'lp-verification.json')['linearProgramsSolved']==617
frozen=read('reports/player-impact-v36/verification.json');assert frozen['passed']
for f,h in frozen['hashes'].items():assert sha(f)==h,f
out={'passed':True,'runtimeChanged':False,'fullOvr':False,'goalComplete':False,'sourceUnsupportedMakesWithPositiveOwnNow':850,'sourceUnsupportedMakesRemaining':41,'previousV36ArtifactsUnchanged':True,
 'scope':'Strict-feasibility allocation prototype, not integrated into engine. All strict source fives checked; 41 unsupported makes in non-strict contexts remain pending. No simulation-accuracy or OVR claim.',
 'hashes':{str(f).replace('\\','/'):sha(f) for f in R.iterdir() if f.is_file() and f.name!='verification.json'}}
(R/'verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))
