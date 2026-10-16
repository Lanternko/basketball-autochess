from pathlib import Path
R=Path('reports/player-impact-v31');O=Path('reports/player-impact-v30')
v=(O/'verify-validation.py').read_text(encoding='utf-8')
v=v.replace("root=Path('reports/player-impact-v30')","root=Path('reports/player-impact-v31')").replace("['v28','control']","['v30','control']").replace("'reports/player-impact-v28/scores.json'","'reports/player-impact-v30/scores.json'").replace("v=='v28'","v=='v30'")
v=v.replace("supplement['trackingFiles']==12","supplement['allProbeEstimatesAndPairedIntervalsRecomputed']")
v=v.replace('previousV28AndControlScoresExactlyReproduced','previousV30AndControlScoresExactlyReproduced')
anchor="status=read(root/'status.json');"
extra="""for name in ['source-verification.json','equivalence-verification.json','profile-verification.json']:
 check=read(root/name);assert check['passed']
 for p,h in check['hashes'].items():assert sha(p)==h,p
"""
assert v.count(anchor)==1;v=v.replace(anchor,extra+anchor)
p=R/'verify-validation.py';assert not p.exists();p.write_text(v,encoding='utf-8')
# Reuse the independent paired-interval arithmetic checker, excluding old passing/tracking work.
s=(O/'verify-supplement.py').read_text(encoding='utf-8')
s=s[:s.index("fp=read(ROOT/'fit-protocol.json')")]
s=s.replace("ROOT=Path('reports/player-impact-v30')","ROOT=Path('reports/player-impact-v31')").replace("read('reports/player-impact-v29/checkpoint.json')","read('reports/player-impact-v30/ovr-probe-checkpoint.json')")
s=s.replace("r['v30']","r['v31']").replace("r['v28']","r['v30']")
s+='''out=dict(passed=True,probePlayers=10,probeGames=9600,allProbeEstimatesAndPairedIntervalsRecomputed=True,
    scope='Fixed-input paired simulation estimates only; no causal or ranking certification.',
    hashes={str(p).replace('\\\\','/'):sha(p) for p in [Path(__file__),ROOT/'ovr-probe-protocol.json',ROOT/'ovr-probe-checkpoint.json',ROOT/'ovr-probe-summary.json']})
(ROOT/'supplement-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='hashes'},indent=2))
'''
p=R/'verify-supplement.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print('Created v31 independent validation and probe arithmetic checks.')
