import json,csv
from pathlib import Path
root=Path('reports/player-box-audit');b=json.loads((root/'baseline.json').read_text(encoding='utf-8'))
for seasons,file in [(b['seasons'],'all-seasons-readable.csv'),([b['seasons'][-1]],'2025-26-readable.csv')]:
    fields=['season','playerId','name','position','positionLowConfidence','minutes','predictedMinutes','minuteDifference']
    keys=list(seasons[0]['players'][0]['metrics'])
    fields += [k+'_'+suffix for k in keys for suffix in ['actual','simulated','difference']]
    with (root/file).open('w',newline='',encoding='utf-8-sig') as f:
      writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
      for s in seasons:
        for p in s['players']:
          row={k:p[k] for k in fields if k in p}
          for k in keys:
            m=p['metrics'].get(k)
            for suffix,v in [('actual',m['actual'] if m else None),('simulated',m['predicted'] if m else None),('difference',m['predicted']-m['actual'] if m else None)]:row[k+'_'+suffix]=round(v,5) if v is not None else ''
          writer.writerow(row)
print('Exported all players; all count statistics per36, percentages percentage points. Low-minute players retained and flagged.')
