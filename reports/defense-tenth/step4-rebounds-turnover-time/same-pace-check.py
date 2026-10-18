import json,pathlib
r=pathlib.Path('reports/defense-tenth/step4-rebounds-turnover-time');rows=[]
for seed in [20261012,20261013,20261014]:
 a=json.loads((r/'runs'/f'2023-24-rawsplit-{seed}.json').read_text(encoding='utf8'));b=json.loads((r/'runs'/f'2023-24-split-{seed}.json').read_text(encoding='utf8'))
 assert a['matches']==b['matches'] and a['teams']==b['teams'] and a['stateTiming']==b['stateTiming']
 rows.append({'season':'2023-24','seed':seed,'games':1230,'scoresStatsAndTimingIdentical':True})
(r/'same-pace-parity.json').write_text(json.dumps(rows,indent=2)+'\n');print('same pace parity',len(rows)*1230)
