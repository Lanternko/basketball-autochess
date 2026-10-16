from pathlib import Path
root=Path('reports/player-impact-v28')
for name in ['validation-score.py','verify-ledgers.mjs']:
 source=Path('reports/player-impact-v26',name).read_text(encoding='utf-8')
 source=source.replace('player-impact-v26','player-impact-v28').replace('player-impact-v25','player-impact-v26').replace("'v25'","'v26'")
 target=root/name;assert not target.exists();target.write_text(source,encoding='utf-8')
print('Created full-season and matched-on-court comparison to v26/control.')
