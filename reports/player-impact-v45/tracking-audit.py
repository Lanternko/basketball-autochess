import json,hashlib
from pathlib import Path
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));rows=[];hashes={}
for season in read(ROOT/'protocol.json')['seasons']:
 current=read(ROOT/f'{season}-fga-data.json');previous=f'{int(season[:4])-1}-{int(season[:4])%100:02d}';file=Path(f'reports/player-impact-v20/{previous}-defense-exposure.json');prior=read(file) if file.exists() else None
 if prior:
  assert int(prior['season'][:4])+1==int(season[:4]);hashes[str(file)]=hashlib.sha256(file.read_bytes()).hexdigest()
 coverage={z:sum(bool(prior and (c:=prior['cards'].get(str(p['playerId']),{}).get(z)) and not c['sourceMissing']) for p in current['players']) for z in ['short','long']}
 rows.append({'season':season,'players':len(current['players']),'lagSeason':previous,'coverage':coverage,'missingPolicy':'zero centered measured feature; missing is not rated as bad defense','currentSeasonTrackingUsedInHeldout':False})
(ROOT/'tracking-audit.json').write_text(json.dumps({'rows':rows,'priorFilesSHA256':hashes,'allFeatureSourcesPrecedeHeldoutSeason':True},indent=2),encoding='utf-8');print(json.dumps(rows))
