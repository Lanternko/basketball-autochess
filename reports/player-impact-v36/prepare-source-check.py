"""Extend the checked source-count reader to independently verify passer marks."""
from pathlib import Path
R=Path('reports/player-impact-v36')
s=Path('reports/player-impact-v35/verify-data.py').read_text(encoding='utf-8').replace("ROOT=Path('reports/player-impact-v35')","ROOT=Path('reports/player-impact-v36')").replace('-conditional-data.json','-marked-data.json')
def replace(a,b):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,b)
replace("for field in ['attempts','selfMakes','assistedMakes','attemptBase','attemptSlope','selfMakeBase','selfMakeSlope','assistedMakeExpected']", "for field in ['attempts','selfMakes','passerMakes','features']")
replace("a,m,n=[row[ix[k]][i] for k in ['attempts','selfMakes','assistedMakes']]", "a,m=row[ix['attempts']][i],row[ix['selfMakes']][i];n=sum(row[ix['passerMakes']][i]);assert row[ix['passerMakes']][i][i]==0")
replace("v=[row[ix[k]][i] for k in ['attemptBase','attemptSlope','selfMakeBase','selfMakeSlope','assistedMakeExpected']]\n   assert all(math.isfinite(x) and x>=0 for x in v) and v[0]>0\n   assert v[2]+v[4]<=v[0]+1e-9 and v[3]<=v[1]+1e-9", "v=row[ix['features']][i];assert len(v)==7 and len(v[6])==5\n   assert all(math.isfinite(x) and x>=0 for x in [*v[:6],*v[6]]) and v[0]>0 and v[1]>0\n   assert abs(v[0]-v[2]-v[4])<1e-9 and abs(v[1]-v[3]-v[5]-sum(v[6]))<1e-9 and v[6][i]==0")
replace("if e.get('shotResult')=='Made':local[tid][pid]['assistedMakes' if e.get('assistPersonId') else 'selfMakes']+=1", "if e.get('shotResult')=='Made':\n     passer=e.get('assistPersonId');local[tid][pid]['assistedMakes' if passer else 'selfMakes']+=1\n     if passer:\n      assert passer in byTeam[tid] and passer!=pid\n      local[tid][pid]['passer_'+str(passer)]+=1")
replace("for k in ['attempts','selfMakes','assistedMakes']:assert row[ix[k]][j]==own[pid][k],(season,key,pid,k)", "for k in ['attempts','selfMakes']:assert row[ix[k]][j]==own[pid][k],(season,key,pid,k)\n     for l,passer in enumerate(row[ix['playerIds']]):assert row[ix['passerMakes']][j][l]==own[pid]['passer_'+str(passer)],(season,key,pid,passer)")
a=s.index("pv=read(ROOT/'probability-verification.json')")
s=s[:a]+'''assert (ROOT/'prepare-data.mjs').read_bytes()==(ROOT/'prepare-marked.mjs').read_bytes()
allHashes[str(Path(__file__)).replace('\\\\','/')]=sha(__file__)
out=dict(passed=True,seasons=seasons,games=sum(s['games'] for s in seasons),sourceStates=sum(s['states'] for s in seasons),freshAttempts=sum(s['freshAttempts'] for s in seasons),
 allCountsAndPasserIdentitiesRejoinedToOriginalPbp=True,strictOwnTotalsExactlyReproduced=True,
 scope='Full original-PBP count and assisted-passer identities plus feature positivity/partition checks. Probability mechanism unchanged from v30, source contexts frozen v30. Not a blind or causal test.',hashes=allHashes)
(ROOT/'marked-data-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['hashes','seasons']},indent=2),flush=True)
'''
(R/'verify-marked-data.py').write_text(s,encoding='utf-8');print('Prepared independent passer-identity source check')
