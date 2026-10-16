"""Calendar/season parameterization of audited player-only four-factor models."""
import json,os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];config=json.loads((R/sys.argv[1]).read_text(encoding='utf-8'));validation=sys.argv[2] if len(sys.argv)>2 else 'forward'
s=(R/'scripts/estimate_defense_fifth.py').read_text(encoding='utf-8')
s=s.replace("cutoff=int(os.environ.get('DEFENSE_FIFTH_CUTOFF','41'))",f"cutoff={config['k']}").replace("out=R/('reports/defense-fifth/model-'+mode)","out=R/config['modelOutput']")
s=s.replace("def read(f): return json.loads((R/f).read_text(encoding='utf-8'))","def path(f):return R/config['paths'].get(f,f)\ndef read(f): return json.loads(path(f).read_text(encoding='utf-8'))")
s=s.replace("assert len(strict)==1188,(len(strict),list(exclude)[:4])","assert strict")
s=s.replace("(R/'reports/defense-b1/stints.jsonl')","path('reports/defense-b1/stints.jsonl')")
s=s.replace("all(order[g,t]<=cutoff for t in (game_map[g]['homeId'],game_map[g]['awayId']))","game_map[g]['date']<=config['date']").replace("order[r['id'],r['team']]>cutoff","game_map[r['id']]['date']>config['date']")
s=s.replace("g41=next(g for g in league['schedule'] if g['id'] in game_map and (g['homeId']==src['teamId'] or g['awayId']==src['teamId']) and order[g['id'],src['teamId']]==cutoff)","g41={'date':config['date']}").replace("assert t['GP']<=cutoff","assert t['GP']<=config['teamGP'][str(src['teamId'])]")
if validation=='forward':
 a=s.index('fold_inputs=[]');b=s.index('A,C,totals=features(train_games)',a)
 s=s[:a]+'''fold_inputs=[]
dates=sorted({game_map[g]['date'] for g in train_games});edges=[dates[int((len(dates)-1)*q)] for q in [.5,2/3,5/6,1]]
for lo,hi in zip(edges[:-1],edges[1:]):
    allowed={g for g in train_games if game_map[g]['date']<=lo};valid={g for g in train_games if lo<game_map[g]['date']<=hi};a,c,_=features(allowed)
    fold_inputs.append((np.array([g in allowed for g in game_ids]),np.array([g in valid for g in game_ids]),a,c))
'''+s[b:]
# Output sources must identify the actual files and wrapper, not hard-coded season.
s=s.replace("(R/f).read_bytes()","path(f).read_bytes()")
exec(compile(s,'calendar-factor-estimator','exec'),dict(config=config,__name__='__main__',__file__=str(R/'scripts/estimate_defense_fifth.py')))
