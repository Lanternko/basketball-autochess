"""Preregister an oracle-lineup, individual-only opportunity-context diagnostic."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
SEASONS=['2022-23','2023-24','2024-25','2025-26']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def table(p):
 t=read(p)['data']['resultSets'][0]
 return [dict(zip(t['headers'],r)) for r in t['rowSet']]

if __name__=='__main__':
 assert not (HERE/'protocol.json').exists(),'Do not overwrite registration'
 sources={};inputs=[];jobs=[]
 for s in SEASONS:
  base='data/season-source' if s=='2025-26' else f'data/defense-seventh/{s}'
  stints='reports/defense-b1' if s=='2025-26' else f'reports/defense-seventh/{s}/stints'
  paths={'teamGames':base+'/team-games.json','playerGames':base+'/player-games.json',
         'stints':stints+'/stints.jsonl','strictAudit':stints+'/defensive-samples.json',
         'fullTracking':f'reports/defense-tenth/step4-rebounds-talent/raw/tracking/{s}-Rebounding.json'}
  games={r['GAME_ID']:r['GAME_DATE'][:10] for r in table(ROOT/paths['teamGames']) if str(r['GAME_ID']).startswith('002')}
  ordered=sorted(games.items(),key=lambda x:(x[1],x[0]));cutoff=ordered[(len(ordered)-1)//2][1]
  nextday=(datetime.fromisoformat(cutoff)+timedelta(days=1)).date().isoformat()
  sources[s]={**paths,'cutoff':cutoff,'nextDay':nextday,'games':len(games)}
  inputs+=list(paths.values())
  for half,start,end in [('first','',cutoff),('second',nextday,'')]:
   jobs.append({'season':s,'half':half,'DateFrom':start,'DateTo':end,
                'file':f'reports/defense-tenth/step4-rebounds-context/raw/{s}-{half}.json'})
 inputs+=['reports/defense-tenth/step4-rebounds-components/analyze.py',
          'reports/defense-tenth/step4-rebounds-components/protocol.json']
 protected={p.relative_to(ROOT).as_posix():sha(p) for scope in ['src','scripts','reports/defense-tenth']
            for p in (ROOT/scope).rglob('*') if p.is_file() and HERE not in p.parents}
 dump(HERE/'protected-before.json',protected)
 p={'version':'oreb-context-offline-1','at':datetime.now(timezone.utc).isoformat(),
    'scope':'Offline diagnostic; no engine/card changes. Finish and stop. Four seen seasons, not blind. Second-half observed lineups are explicit oracle conditions, never called preseason forecasts.',
    'sources':sources,'inputHashes':{f:sha(ROOT/f) for f in inputs},
    'protectedSHA256':sha(HERE/'protected-before.json'),'registerSHA256':sha(Path(__file__)),
    'acquisition':{'jobs':jobs,'endpoint':'https://stats.nba.com/stats/leaguedashptstats',
       'PtMeasureType':'Rebounding','concurrency':2,'attempts':2,'timeoutMS':15000,
       'integrity':'Audit echoed dates, player GP <= corresponding official box appearances, nonempty table, no duplicate IDs; first+second OREB and chances reconcile to cached full-season within1% summed absolute difference. If a season fails, no fitting/evaluation for it; missing older training seasons stops fit rather than substituting latest seasons.'},
    'cutoff':'One league calendar date, the date of median regular-season game; every game on cutoff belongs to first half. Cup final excluded by official002 regular-season games. No per-team K.',
    'context':{
       'role':'First-half individual AST/36 determines order among five. Proxy leader share is stint-time fraction with focal highest AST/36; exact ties split1/n. Do not call it observed ballhandling or starting PG.',
       'competition':'Stint-time weighted sum of OTHER FOUR players first-half tracking OREB_CHANCES/36. Same first-half profiles used for both halves; focal omitted. Missing/new players use prefix league median, never second-half rates.',
       'lineups':'Use existing strict-game lineups. Exclude missingPbp, lineupFailed, uncertainPossessionGames, counterMismatchGames. Strict game counts must match prior audit. No coordinates manufactured.',
       'features':'Own first-half chance36, log1p(first-half box MIN), first-half AST36; independent additions deltaRole (second-first), deltaCompetition (second-first). These deltas use known later membership/time but only prefix individual traits. No post abilities, team efficiency, on-off or outcomes as features.',
       'confounding':'Within-person changes remove fixed person differences, not time-varying scheme, shot mix, misses, injury or teammate selection. Opportunity is period aggregate, not per-lineup chance labels.'},
    'cohort':{'MIN':200,'trackingMIN':100,'firstHalfChances':10,'strictMinuteFraction':.70,
       'rule':'Both halves meet box and tracking MIN; first tracking chances>=10; valid raw conversion[0,1]; valid second chance/36. Existing strict stints cover>=70% box MIN in each half. Tracking-missing rows not silently counted as zeros; all exclusions listed.'},
    'estimator':{'train':['2022-23','2023-24'],'test':['2024-25','2025-26'],
       'type':'Ridge predicts second-minus-first chance36; intercept unpenalized; train-only imputation/scaling; grouped five-fold player SHA256 modulo5 CV; larger lambda on tie.',
       'grid':[.1,1,10,100,1000],'weight':'min(second-half box MIN,1000) normalized; test MIN used for evaluation only.',
       'clip':'Predicted chance36>=0. Derived OREB36=predicted chance36*first-half raw conversion; no second conversion, clipping multipliers or result calibration.'},
    'models':{'boxPersistence':'First-half box OREB36, OREB outcome only.',
       'chancePersistence':'First-half chance36; derived rate is first-half tracking OREB36.',
       'history':'Chance delta predicted from own first chance36, logMIN, AST36.',
       'role':'History + deltaRole','competition':'History + deltaCompetition','both':'History + both changes'},
    'metrics':'Second-half chance36 and box OREB36 MAE/RMSE weighted by second box MIN; tests pooled equal season weights, Pearson descriptive. No team net/wins metric or engine adoption.',
    'descriptive':'Each season weighted correlation and slope of within-player chance change vs role/competition changes; roleUp>=.15, roleDown<=-.15; competitionUp>=1 and down<=-1 chance36. Descriptive only. List known trade/mover groups via half maximum-minute teams, not causal trade estimate.',
    'uncertainty':{'replicates':20000,'seed':20261057,'scheme':'Paired franchise resampling crossed Poisson1 individual weights, common franchise and player weights across seasons/models; no simulation seed or training-refit uncertainty.',
       'primary':'Six pooled TEST OREB36 MAE comparisons: role/competition/both vs boxPersistence and history;95% plus Bonferroni99.1667%. All other comparisons exploratory.'},
    'decision':'A context candidate supported only if pooled held-out OREB36 MAE Bonferroni intervals wholly negative vs BOTH references, chanceMAE95 not significantly worse vs history, and each test-season/mover OREB36 MAE95 not significantly worse vs boxPersistence. Even success is oracle-context evidence, not a causal participation coefficient or engine adoption.',
    'geometryInventory':'Inspect first3 sorted PBP file names per season for coordinate fields; count per-action x/y and whether ten-player position trajectories exist. Sampling only, no claim of full-data spatial completeness.'}
 dump(HERE/'protocol.json',p)
 (HERE/'protocol.sha256').write_text(sha(HERE/'protocol.json')+'  protocol.json\n',encoding='utf-8')
 print(json.dumps({'at':p['at'],'sha256':sha(HERE/'protocol.json'),'protected':len(protected),'cutoffs':{s:x['cutoff'] for s,x in sources.items()}}))
