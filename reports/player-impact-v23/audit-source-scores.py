"""Check source score strings before using endgame eligibility; no source changes."""
import json
from pathlib import Path

root = Path('reports/player-impact-v23')
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

out = {}
for season in ['2022-23', '2023-24', '2024-25', '2025-26']:
    source = read(root / f'{season}-putback-choices.json')
    manifest = read(('data/defense-a-source' if season == '2025-26' else f'data/defense-seventh/{season}') + '/manifest.json')
    paths = {g['id']: g['file'] for g in manifest['sources']}
    checked, invalid = 0, []
    for game in source['games']:
        actions = read(paths[game['id']])['data']['game']['actions']
        for row in game['rows']:
            event = actions[row['index']]
            checked += 1
            for key in ['scoreHome', 'scoreAway']:
                value = event.get(key)
                try:
                    valid = value is not None and str(value).strip() != '' and float(value) >= 0 and float(value).is_integer()
                except (ValueError, TypeError):
                    valid = False
                if not valid:
                    invalid.append({'game': game['id'], 'index': row['index'], 'key': key, 'value': value})
    out[season] = {'checkedRebounds': checked, 'invalid': invalid}
    print(season, checked, 'invalid', len(invalid), flush=True)
(root / 'source-score-audit.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
assert all(not v['invalid'] for v in out.values())
