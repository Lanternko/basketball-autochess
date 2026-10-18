"""Post-hoc stronger-benchmark intervals; saved predictions only, no refitting."""
import numpy as np
from analyze import read, intervals
from register import HERE, dump

if __name__ == '__main__':
    p = read(HERE / 'protocol.json')
    predictions = read(HERE / 'predictions.json')
    out = {'label': '事後補充：對原樣沿用前季的較強對照；不重訓、不選模型、不變更驗收。',
           'uncertainty': p['prediction']['uncertainty'], 'results': {}}
    for outcome in ['rate', 'pct']:
        label = 'cross2025-' + outcome
        out['results'][label] = {}
        for group in ['all', 'movers', 'lowSourceMinutes']:
            rows = [r for r in predictions[label] if group == 'all' or
                    (group == 'movers' and r['mover']) or
                    (group == 'lowSourceMinutes' and r['sourceMinutes'] < 500)]
            # intervals() names its reference history; relabel the reference explicitly below.
            preds = {'history': np.array([r['predictions']['persistence'] for r in rows])}
            preds.update({m: np.array([r['predictions'][m] for r in rows])
                          for m in ['static', 'talent', 'behavior']})
            x = intervals(rows, preds, p, outcome)
            x['reference'] = 'persistence: raw prior outcome, not fitted history'
            x['versions']['persistence'] = x['versions'].pop('history')
            x['paired'] = {k.replace('MinusHistory', 'MinusPersistence'): v for k, v in x['paired'].items()}
            out['results'][label][group] = x
    dump(HERE / 'persistence-supplement.json', out)
    print('Saved post-hoc stronger-benchmark intervals; no model or prediction changed.')
