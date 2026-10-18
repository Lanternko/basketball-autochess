import json,hashlib,re
from pathlib import Path
from collections import defaultdict,Counter
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(f,x):(O/f).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def table(p):
 t=read(p)['data']['resultSets'][0];return [dict(zip(t['headers'],r)) for r in t['rowSet']]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
protocol=read(O/'protocol.json');assert sha(O/'protocol.json')==(O/'protocol.sha256').read_text().split()[0]
seasons=protocol['seasons'];old=read(R/'reports/defense-tenth/step4-t2/players.json');oldcases=read(R/'reports/defense-tenth/step4-t2-supplement/cases.json');oldbins=read(R/'reports/defense-tenth/step4-t2-supplement/lineup-observations.json')
profiles={};logs={};teamlogs={};bygame={};org={};sourcehash={}
for season in seasons:
 base=R/('data/season-source' if season=='2025-26' else f'data/defense-seventh/{season}')
 rows=table(base/'player-games.json');logs[season]=rows;teamlogs[season]=table(base/'team-games.json');group=defaultdict(list);bg=defaultdict(list)
 for row in rows:group[str(row['TEAM_ID']),str(row['PLAYER_ID'])].append(row);bg[row['GAME_ID']].append(row)
 bygame[season]=bg;profiles[season]={};org[season]={}
 advanced={str(x['PLAYER_ID']):x for x in table(R/f'reports/defense-tenth/step4-t2/raw/{season}/0-advanced.json')}
 for (tid,pid),rr in group.items():
  mins=sum(r['MIN'] or 0 for r in rr);gp=len(rr);asts=sum(r['AST'] or 0 for r in rr);a=advanced.get(pid,{})
  profiles[season][tid+':'+pid]={'teamId':int(tid),'id':int(pid),'name':rr[0]['PLAYER_NAME'],'MIN':mins,'GP':gp,'AST':asts,'ASTperMIN':asts/mins if mins else 0,'AGE':a.get('AGE'),'AST_PCT':a.get('AST_PCT'),'USG_PCT':a.get('USG_PCT')}
 for tid in old[season]['teams']:
  pool=[x for x in profiles[season].values() if str(x['teamId'])==tid and x['MIN']>=500 and x['MIN']/x['GP']>=20]
  if pool:org[season][tid]=max(pool,key=lambda x:(x['ASTperMIN'],x['AST'],-x['id']))
 sourcehash[str(base/'player-games.json')]=sha(base/'player-games.json')
save('profiles.json',profiles);save('organizers.json',org)
out=[];overall=[];coverage=[];errata=[]
for si,season in enumerate(seasons):
 base=R/('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')
 sf=R/('reports/defense-b1' if season=='2025-26' else f'reports/defense-seventh/{season}/stints')
 audit=read(sf/'defensive-samples.json');excluded={g if isinstance(g,str) else g['id'] for k in ['missingPbp','lineupFailed','uncertainPossessionGames','counterMismatchGames'] for g in audit[k]}
 valid=set()
 for line in (sf/'real-games.jsonl').open(encoding='utf8'):
  g=json.loads(line)
  if g['id'] not in excluded and g['lineupsValid'] and g['pointsValid'] and not g['anomalies']:valid.add(g['id'])
 assert len(valid)==audit['strictUsableGames']
 stints=defaultdict(list);defcounts=Counter();rbins=defaultdict(lambda:[0.,0.]);expectedreb=Counter()
 cards={str(p['playerId']):p for t in read(R/f'reports/defense-tenth/step4-t0/{season}/bundle.json')['league']['teams'] for p in t['roster']}
 caseids={str(c['teamId']) for c in oldcases if c['season']==season}
 def rim(pid):
  p=old[season]['players'].get(str(pid));c=cards.get(str(pid),{})
  return c.get('heightInches',0)>=82 and p is not None and (p['metrics'].get('BLK36') or 0)>=1 and p['samples'].get('rimFGA',0)>=100 and (p['metrics'].get('rimSuppression') or 0)>0
 for line in (sf/'stints.jsonl').open(encoding='utf8'):
  st=json.loads(line)
  if st['id'] not in valid:continue
  stints[st['id']].append(st)
  for t in st['teams']:
   tid=str(t['teamId']);d=t['opponent']['dreb'];a=t['opponent']['oreb'];defcounts[tid]+=d
   if tid in caseids:
    for kind,n in [('rimProtector',sum(rim(pid) for pid in t['players'])),('sizeOnly',sum(cards.get(str(pid),{}).get('heightInches',0)>=82 for pid in t['players']))]:
     rbins[tid,kind,min(2,n)][0]+=d;rbins[tid,kind,min(2,n)][1]+=a
 for t in teamlogs[season]:
  if t['GAME_ID'] in valid:expectedreb[str(t['TEAM_ID'])]+=t['DREB']
 assert all(defcounts[k]==v for k,v in expectedreb.items()),'DREB semantic check'
 for c in oldcases:
  if c['season']!=season:continue
  tid=str(c['teamId']);d=sum(v[0] for k,v in rbins.items() if k[0]==tid and k[1]=='rimProtector');a=sum(v[1] for k,v in rbins.items() if k[0]==tid and k[1]=='rimProtector')
  errata.append({'season':season,'team':c['team'],'type':'teamStrict','oldDREBpct':c['observed']['DREBpct'],'correctDREBpct':100*d/(d+a) if d+a else None,'dreb':d,'opponentOreb':a})
  for x in oldbins:
   if x['season']!=season or x['team']!=c['team']:continue
   d,a=rbins[tid,x['type'],x['count']]
   errata.append({'season':season,'team':c['team'],'type':x['type'],'count':x['count'],'oldDREBpct':x['stats']['DREBpct'],'correctDREBpct':100*d/(d+a) if d+a else None,'dreb':d,'opponentOreb':a})
 grouped=defaultdict(Counter);totals=defaultdict(Counter);matched=0;allfg=0;strictfg=0;unmatched=[];badassist=0;pbpsources=read(base/'manifest.json')['sources'];gameaudits=[]
 for source in pbpsources:
  path=R/source['file'];assert sha(path)==source['sha256'];actions=read(path)['data']['game']['actions'];gid=source['id'];raw=Counter();strr=stints.get(gid,[]);index={}
  for st in strr:
   for i in range(st['startIndex'],st['endIndex']):
    assert i not in index or index[i]['period']!=st['period'];index[i]=st
  played=defaultdict(set)
  for x in bygame[season][gid]:
   if (x['MIN'] or 0)>0:played[str(x['TEAM_ID'])].add(str(x['PLAYER_ID']))
  for i,e in enumerate(actions):
   if not e.get('isFieldGoal') or e['actionType'] not in ['2pt','3pt']:continue
   pid=str(e['personId']);tid=str(e['teamId']);made=int(e['shotResult']=='Made');assisted=int(bool(e.get('assistPersonId')));zone='three' if e['actionType']=='3pt' else 'mid' if e.get('area')=='Mid-Range' else 'paint';pull=int(bool(re.search(r'pull[ -]?up',' '.join(str(e.get(k,'')) for k in ['descriptor','subType','description']),re.I)))
   raw[tid,'FGA']+=1;raw[tid,'FGM']+=made;allfg+=1
   if made and e.get('assistPlayerNameInitial') and not assisted:badassist+=1
   counts={'a':1,'m':made,'am':made*assisted,'pullA':pull,'pullM':pull*made}
   totals[tid,pid,zone].update(counts)
   if gid not in valid:continue
   strictfg+=1;st=index.get(i)
   offense=next((t for t in st['teams'] if str(t['teamId'])==tid),None) if st and st['period']==e['period'] else None
   if not offense or int(pid) not in offense['players']:
    unmatched.append({'game':gid,'actionIndex':i,'player':pid});continue
   matched+=1
   for kind,anchor in [('current',org[season].get(tid)),('prior',org[seasons[si-1]].get(tid) if si else None)]:
    if not anchor or anchor['id']==int(pid) or str(anchor['id']) not in played[tid]:continue
    on=int(anchor['id'] in offense['players']);grouped[gid,tid,kind,anchor['id'],pid,zone,on].update(counts)
  for tr in (r for r in teamlogs[season] if r['GAME_ID']==gid):
   gameaudits.append({'id':gid,'team':tr['TEAM_ID'],'fgaDifference':raw[str(tr['TEAM_ID']),'FGA']-tr['FGA'],'fgmDifference':raw[str(tr['TEAM_ID']),'FGM']-tr['FGM']})
 for key,c in grouped.items():
  gid,tid,kind,anchor,pid,zone,on=key;out.append({'season':season,'game':gid,'team':int(tid),'kind':kind,'organizer':anchor,'player':int(pid),'zone':zone,'on':on,**c})
 for (tid,pid,zone),c in totals.items():overall.append({'season':season,'team':int(tid),'player':int(pid),'zone':zone,**c})
 coverage.append({'season':season,'sourceGames':len(pbpsources),'strictGames':len(valid),'allFGA':allfg,'strictFGA':strictfg,'matchedFGA':matched,'unmatched':unmatched,'missingAssistIdOnNamedAssistedMake':badassist,'boxDifferences':[g for g in gameaudits if g['fgaDifference'] or g['fgmDifference']],'defensiveReboundSchemaCheck':'exact all strict team DREB vs official boxes'})
 sourcehash[str(sf/'stints.jsonl')]=sha(sf/'stints.jsonl');sourcehash[str(base/'manifest.json')]=sha(base/'manifest.json')
 print('PBP',season,len(pbpsources),len(valid),strictfg,matched,len(grouped),flush=True)
save('onoff-game-counts.json',out);save('overall-pbp-counts.json',overall);save('pbp-coverage.json',coverage);save('input-hashes.json',sourcehash)
save('t2-rebound-erratum.json',{'cause':'opponent.dreb already belongs to defending team per prepare_defense_b1.js:36-39; previous supplement incorrectly used other team value','oldFilesUnchanged':True,'affected':'strict observed and binned DREBpct only; full-season box/sim metrics unchanged','rows':errata})
