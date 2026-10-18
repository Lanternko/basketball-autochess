import json,hashlib,math,subprocess
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v28');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
checked={}
def hashes(x):
 for p,h in x['hashes'].items():
  if p not in checked:checked[p]=sha(p)
  assert checked[p]==h,p
hashes(read(root/'validation-protocol.json'))
fg=oreb=states=players=0;seasons=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 a=read(root/f'{season}-oreb-risksets.json');hashes(a);counts=a['counts'];t=read(f'reports/player-impact-v1/{season}-on-court-truth.json')
 assert {g['id'] for g in a['games']}==set(t['gameIds'])
 assert counts['allReboundEvents']==counts['teamRebounds']+counts['allIndividualOreb']+counts['allIndividualDreb']
 assert counts['allIndividualOreb']+counts['allIndividualDreb']==counts['individualFgRebounds']+counts['individualFtRebounds']+counts.get('individualOtherShotReference',0)
 sums=defaultdict(Counter);expected=0;n=o=0
 for g in a['games']:
  indices=set()
  for r in g['rows']:
   assert r['index'] not in indices;indices.add(r['index']);assert len(set(r['own']))==len(set(r['opponent']))==5
   assert not set(r['own']) & set(r['opponent']);assert len(r['weights'])==5 and 0<=r['selected']<=5
   assert math.isclose(sum(r['weights']),1,abs_tol=1e-12);assert .05<=r['pFresh']<=.6
   # Fatigue currently modifies only long/mid/short/drive: no rebate/defense
   # fatigue mechanism exists in this version, so these must be identical.
   assert r['pEnergy']==r['pFresh'];n+=1;o+=r['selected']<5;expected+=r['pFresh']
   for j,pid in enumerate(r['own']):
    p=sums[pid];p['fgChances']+=1;p['fgOreb']+=r['selected']==j;p['expectedFresh']+=r['pFresh']*r['weights'][j]
    if r['selected']<5:p['teamWonChances']+=1;p['expectedConditional']+=r['weights'][j]
 assert n==counts['individualFgRebounds'] and o==counts['individualFgOreb']
 assert math.isclose(expected,a['expectedTeamOreb']['fresh'],abs_tol=1e-7)
 for p in a['players']:
  for k in ['fgChances','fgOreb','expectedFresh','expectedConditional','teamWonChances']:assert math.isclose(p[k],sums[p['playerId']][k],abs_tol=1e-8)
  assert p['expectedFresh']==p['expectedEnergy']
 assert not a['issues'] if season!='2025-26' else len(a['issues'])==8 and all(p['shotAction']=='heave' for p in a['issues'])
 if season=='2025-26':
  basic=read('reports/player-impact-v27/2025-26-strict-basic-truth.json');by={p['playerId']:p for p in basic['players']}
  for p in a['players']:assert p['allOreb']==by[p['playerId']]['stats']['oreb']
 new=read(root/f'{season}-contexts.json');old=read(f'reports/player-impact-v20/{season}-contexts.json')
 for k in ['stints','states','strictMinutes','contextReference']:assert new[k]==old[k]
 for pid,c in new['cards'].items():
  for k in ['strictSeconds','meanSourceShootingMultiplier','sourceZoneAttempts']:assert c[k]==old['cards'][pid][k]
  assert all(math.isfinite(v) for d in c['contexts'].values() for v in d.values())
 mapping={'stintsSHA256':new['sources']['stints'],'shotExposureSHA256':f'reports/player-impact-v17/{season}-shot-exposures.json','codeSHA256':str(root/'prepare-contexts-v2.mjs'),'defenseAnchorSHA256':str(root/'defense-input.mjs'),'inputSHA256':'reports/player-impact-v20/role-input.mjs','exposureDefenseModelSHA256':str(root/'model.mjs'),'defenseExposureSHA256':f'reports/player-impact-v20/{season}-defense-exposure.json'}
 for k,p in mapping.items():assert sha(p)==new['sources'][k],(k,p)
 fg+=n;oreb+=o;states+=new['states'];players+=len(a['players']);seasons.append({'season':season,'individualFgRebounds':n,'fgOreb':o,'issues':len(a['issues']),'oldFgOreb36MAE':a['maeFgOreb36']['fresh']})
assert (fg,oreb,players)==(365784,93950,2262)
defense=read(root/'defense-curve-audit.json');hashes(defense);restored=0
for s in defense['seasons']:
 for p in s['rows']:
  assert math.isclose(p['sourcePosterior'],p['sourceDifference']*p['attempts']/(p['attempts']+200),abs_tol=1e-12)
  if abs(p['difference'])>1e-8:restored+=1;assert p['attribute']==99 and p['zone']=='short'
assert restored==12
fallback=read(root/'fallback-parity.json');hashes(fallback);assert fallback['passed'] and fallback['games']==96
test=subprocess.run(['node','test/defense_source_roundtrip.js'],text=True,capture_output=True,check=True)
out={'passed':True,'sourceHashFiles':len(checked),'individualFgRebounds':fg,'individualFgOreb':oreb,'sourceContextStates':states,'playerSeasons':players,'restoredSourcePlayerZoneCards':restored,'fallbackExactV26Games':96,'test':test.stdout.strip(),'seasons':seasons,'scope':'Source counts/provenance/round-trip correction and rebuilt contexts only. Does not certify ordinary simulation accuracy, OVR or adoption.'}
(root/'source-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
