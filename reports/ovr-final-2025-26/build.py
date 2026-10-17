"""Final 2025-26 OVR for real players: box-prior RAPM mapped to the 40-99 display scale.

  python3 reports/ovr-final-2025-26/build.py [--source lastSeason|pooled] [--input PATH]

Input: reports/impact-rapm/rapm-prior.csv from
  python3 reports/impact-rapm/rapm.py --prior reports/ovr-rapm-calibrated-2025-26/priors.csv
Default source is the 2025-26-only box-prior RAPM (the season the cards represent; its
held-out error improved most with the prior). Players present in 2025-26 data only.

Scale: among players with >= 500 minutes in 2025-26, PR1 = 40, PR50 = 70, PR99 = 99,
linear between anchors and extended with the PR50-PR99 slope above 99, the same rule as
the baseball calculator and the other prototypes. Minutes are used only to pick the
reference pool, never to raise or lower a player's value (no availability deduction).
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
SCALE_MIN_MINUTES = 500


def arg(name, default):
    return sys.argv[sys.argv.index('--' + name) + 1] if '--' + name in sys.argv else default


def main():
    source = arg('source', 'lastSeason')
    path = Path(arg('input', ROOT / 'reports/impact-rapm/rapm-prior.csv'))
    league = json.loads((ROOT / 'data/season-league.json').read_text(encoding='utf-8'))
    season = {}
    for t in league['teams']:
        for p in t['roster']:
            s = season.setdefault(p['playerId'], {'name': p['name'], 'pos': p['pos'], 'MIN': 0.0, 'teams': []})
            s['MIN'] += p['observed']['MIN']; s['teams'].append(t['name'])
    rows = []
    for r in csv.DictReader(open(path, encoding='utf-8')):
        pid = int(r['playerId'])
        if pid not in season:
            continue
        s = season[pid]
        rows.append({'playerId': pid, 'name': s['name'], 'pos': s['pos'], 'teams': ' / '.join(s['teams']), 'MIN': s['MIN'],
                     'net': float(r[source + 'Net']), 'O': float(r[source + 'O']), 'D': float(r[source + 'D']),
                     'priorO': r['priorO'], 'priorD': r['priorD']})
    missing = sorted(set(season) - {r['playerId'] for r in rows})
    ref = sorted(r['net'] for r in rows if r['MIN'] >= SCALE_MIN_MINUTES)
    q = lambda pr: ref[int(round(pr / 100 * (len(ref) - 1)))]
    p1, p50, p99 = q(1), q(50), q(99)
    for r in rows:
        x = r['net']
        r['ovr'] = 40 + 30 * (x - p1) / (p50 - p1) if x <= p50 else 70 + 29 * (x - p50) / (p99 - p50)
    rows.sort(key=lambda r: -r['net'])
    with open(OUT / 'ranking.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['rank', 'ovr', 'playerId', 'name', 'pos', 'teams', 'MIN', 'netPer100', 'offensePer100', 'defensePer100', 'boxPriorO', 'boxPriorD'])
        for k, r in enumerate(rows):
            w.writerow([k + 1, round(r['ovr']), r['playerId'], r['name'], r['pos'], r['teams'], round(r['MIN']),
                        round(r['net'], 2), round(r['O'], 2), round(r['D'], 2), r['priorO'], r['priorD']])
    summary = {'source': source, 'input': str(path), 'players': len(rows), 'missingFromInput': len(missing),
               'scaleAnchorsNetPer100': {'PR1': p1, 'PR50': p50, 'PR99': p99},
               'top25': [(r['name'], round(r['ovr']), round(r['net'], 2)) for r in rows[:25]]}
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=1))


main()
