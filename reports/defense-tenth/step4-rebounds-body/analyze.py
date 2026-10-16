"""Existing-input audit only. Does not construct cards or invoke a simulator."""
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

from register import ROOT, HERE, sha, dump


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def table(doc):
    if not isinstance(doc, dict) or not isinstance(doc.get('data', {}), dict):
        return [], []
    datasets = doc.get('data', {}).get('resultSets', [])
    if isinstance(datasets, dict):
        datasets = [datasets]
    if not datasets:
        return [], []
    dataset = datasets[0]
    headers = dataset.get('headers', [])
    if not all(isinstance(k, str) for k in headers):
        return [], headers
    return [dict(zip(headers, row)) for row in dataset.get('rowSet', [])], headers


def positive(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) and number > 0 else None
    except (ValueError, TypeError):
        return None


def coverage(rows, key):
    observed = [r for r in rows if positive(r.get(key)) is not None]
    total_minutes = sum(r['minutes'] for r in rows)
    return {'observedPlayers': len(observed), 'players': len(rows),
            'playerCoverage': len(observed) / len(rows) if rows else None,
            'minuteCoverage': sum(r['minutes'] for r in observed) / total_minutes if total_minutes else None}


def correlation(rows, a, b):
    valid = [(positive(r.get(a)), positive(r.get(b))) for r in rows]
    valid = [(x, y) for x, y in valid if x is not None and y is not None]
    if len(valid) < 3:
        return {'n': len(valid), 'Pearson': None, 'Spearman': None}
    x, y = np.array(valid).T
    return {'n': len(valid), 'Pearson': float(np.corrcoef(x, y)[0, 1]),
            'Spearman': float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])}


def attribute(percentile):
    return max(40, min(99, 40 + (percentile - 1) * 30 / 49
                       if percentile < 50 else 70 + (percentile - 50) * 29 / 49))


def legacy_rank(value, pool):
    if value is None or not pool:
        return 70
    return attribute(100 * (sum(v < value for v in pool) + .5 * sum(v == value for v in pool)) / len(pool))


def scan_candidates():
    tokens = ('bio', 'combine', 'anthro', 'measurement', 'player-info', 'player_info',
              'commonplayer', 'draft', 'physical')
    result = []
    for scope in ['data', 'reports']:
        for folder, dirs, files in os.walk(ROOT / scope):
            dirs[:] = [d for d in dirs if d not in ['runs', 'pbp', 'node_modules', HERE.name]]
            for name in sorted(files):
                if not name.endswith('.json') or not any(t in name.lower() for t in tokens):
                    continue
                path = Path(folder) / name
                doc = read(path)
                _, headers = table(doc)
                result.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
                               'bytes': path.stat().st_size, 'rawNBADataSet': bool(headers),
                               'headers': headers, 'topLevelKeys': list(doc) if isinstance(doc, dict) else [],
                               'url': doc.get('url') if isinstance(doc, dict) else None})
    return result


def run():
    protocol = read(HERE / 'protocol.json')
    expected = (HERE / 'protocol.sha256').read_text(encoding='utf-8').split()[0]
    assert sha(HERE / 'protocol.json') == expected, 'Protocol changed'
    for path, digest in protocol['inputHashes'].items():
        assert sha(ROOT / path) == digest, f'Input changed: {path}'
    lock = read(HERE / 'analysis-code-registration.json')
    for path, digest in lock['hashes'].items():
        assert sha(ROOT / path) == digest, f'Analysis code/input changed: {path}'

    inventory = scan_candidates()
    reports, records, all_fields = [], {}, {}
    for season in protocol['seasons']:
        raw_folder = ROOT / 'data/defense-seventh' / season
        bio_path = ROOT / 'data/benchmark-source/bio.json' if season == '2025-26' else raw_folder / 'bio.json'
        log_path = ROOT / 'data/season-source/player-games.json' if season == '2025-26' else raw_folder / 'player-games.json'
        bio_doc, log_doc = read(bio_path), read(log_path)
        assert bio_doc['season'] == season and log_doc['season'] == season
        bios, headers = table(bio_doc)
        logs, _ = table(log_doc)
        bios_by_id = defaultdict(list)
        for r in bios:
            bios_by_id[r['PLAYER_ID']].append(r)
        totals = {}
        for row in logs:
            r = totals.setdefault(row['PLAYER_ID'], {'playerId': row['PLAYER_ID'], 'name': row['PLAYER_NAME'],
                                                     'minutes': 0, 'GP': 0})
            r['minutes'] += row.get('MIN') or 0
            r['GP'] += 1
        bundle_path = ROOT / f'reports/defense-tenth/step4-t0/{season}/bundle.json'
        bundle = read(bundle_path)
        card_lists = defaultdict(list)
        for team in bundle['league']['teams']:
            for p in team['roster']:
                card_lists[p['playerId']].append(p)
        all_fields[season] = sorted({key for group in card_lists.values() for p in group for key in p})
        duplicate_conflicts, bio_conflicts, cohort = [], [], []
        fields = ['heightInches', 'bodyWeight', 'physique', 'stamina']
        for player in sorted(totals.values(), key=lambda q: q['playerId']):
            if player['minutes'] <= 0:
                continue
            pid = player['playerId']
            cards, rs = card_lists.get(pid, []), bios_by_id.get(pid, [])
            if any(len({str(p.get(k)) for p in cards}) > 1 for k in fields):
                duplicate_conflicts.append({'id': pid, 'name': player['name'], 'values': [{k: p.get(k) for k in fields} for p in cards]})
            if any(len({str(r.get(k)) for r in rs}) > 1 for k in ['PLAYER_HEIGHT_INCHES', 'PLAYER_WEIGHT']):
                bio_conflicts.append({'id': pid, 'rows': rs})
            card, bio = (cards[0] if cards else {}), (rs[0] if rs else {})
            h, w = positive(bio.get('PLAYER_HEIGHT_INCHES')), positive(bio.get('PLAYER_WEIGHT'))
            raw_size = h + w / 10 if h and w else None
            dh, dw = positive(card.get('heightInches')), positive(card.get('bodyWeight'))
            r = {**player, 'rotation': player['GP'] >= 30 and player['minutes'] / player['GP'] >= 20,
                 'rawHeightInches': h, 'rawWeightLb': w, 'rawHeightString': bio.get('PLAYER_HEIGHT'),
                 'rawWeightString': bio.get('PLAYER_WEIGHT'), 'rawSizeIndex': raw_size,
                 'deployedHeightInches': dh, 'deployedWeightLb': dw,
                 'deployedPhysique': positive(card.get('physique')),
                 'deployedStamina': positive(card.get('stamina')),
                 'deployedSizeIndex': dh + dw / 10 if dh and dw else None,
                 'cardMissing': not bool(cards), 'sourceBioMissing': not bool(rs),
                 'wingspanInches': None, 'standingReachInches': None,
                 'strengthMeasurement': None, 'standingVerticalInches': None, 'maxVerticalInches': None,
                 'measurementDate': None, 'availabilityDate': None, 'sourceFetchedAt': bio_doc.get('fetchedAt'),
                 'source': bio_path.relative_to(ROOT).as_posix(),
                 'status': 'Recorded seasonal-query metadata; measurement date and contemporaneous availability unverified. Not a new card.'}
            cohort.append(r)
        pool = [r for r in cohort if r['rotation'] and
                (r['rawWeightLb'] if season == '2025-26' else r['deployedWeightLb'])]
        pool_values = [r['rawSizeIndex'] if season == '2025-26' else r['deployedSizeIndex'] for r in pool]
        assert all(v is not None for v in pool_values)
        rank_mismatches, raw_height_mismatches, raw_weight_mismatches = [], [], []
        for r in cohort:
            idx = r['rawSizeIndex'] if season == '2025-26' else r['deployedSizeIndex']
            weight = r['rawWeightLb'] if season == '2025-26' else r['deployedWeightLb']
            reconstructed = legacy_rank(idx, pool_values) if weight else 70
            r['legacyPhysiqueReconstructed'] = reconstructed
            if r['deployedPhysique'] is None or abs(reconstructed - r['deployedPhysique']) > 1e-8:
                rank_mismatches.append({'id': r['playerId'], 'name': r['name'], 'deployed': r['deployedPhysique'], 'reconstructed': reconstructed})
            if r['rawHeightInches'] is not None and r['deployedHeightInches'] != r['rawHeightInches']:
                raw_height_mismatches.append({'id': r['playerId'], 'name': r['name'], 'raw': r['rawHeightInches'], 'card': r['deployedHeightInches']})
            if r['rawWeightLb'] is not None and r['deployedWeightLb'] is not None and r['rawWeightLb'] != r['deployedWeightLb']:
                raw_weight_mismatches.append({'id': r['playerId'], 'name': r['name'], 'raw': r['rawWeightLb'], 'card': r['deployedWeightLb']})
        missing_raw = [{k: r[k] for k in ['playerId', 'name', 'minutes', 'GP', 'rawHeightInches', 'rawWeightLb',
                                         'deployedHeightInches', 'deployedWeightLb', 'deployedPhysique']}
                       for r in cohort if r['rawHeightInches'] is None or r['rawWeightLb'] is None]
        report = {'season': season, 'players': len(cohort), 'minutes': sum(r['minutes'] for r in cohort),
                  'rotationPlayers': sum(r['rotation'] for r in cohort),
                  'zeroMinuteIds': [r for r in totals.values() if r['minutes'] <= 0],
                  'bioSource': bio_path.relative_to(ROOT).as_posix(), 'bioURL': bio_doc.get('url'),
                  'bioFetchedAt': bio_doc.get('fetchedAt'), 'bioHeaders': headers,
                  'coverage': {key: coverage(cohort, key) for key in ['rawHeightInches', 'rawWeightLb',
                               'deployedHeightInches', 'deployedWeightLb', 'wingspanInches', 'standingReachInches',
                               'strengthMeasurement', 'standingVerticalInches', 'maxVerticalInches']},
                  'missingRawBody': missing_raw, 'rawHeightMismatches': raw_height_mismatches,
                  'rawWeightMismatches': raw_weight_mismatches, 'duplicateCardConflicts': duplicate_conflicts,
                  'duplicateBioConflicts': bio_conflicts, 'rankReconstructionMismatches': rank_mismatches,
                  'correlations': {f'{a} vs {b}': correlation(cohort, a, b) for a, b in [
                      ('rawHeightInches', 'rawWeightLb'), ('rawHeightInches', 'deployedPhysique'),
                      ('rawWeightLb', 'deployedPhysique'), ('rawSizeIndex', 'deployedPhysique')]}}
        reports.append(report)
        records[season] = cohort

    transitions = []
    for a, b in zip(protocol['seasons'], protocol['seasons'][1:]):
        before = {r['playerId']: r for r in records[a]}
        pairs = [(before[r['playerId']], r) for r in records[b] if r['playerId'] in before]
        changes = {}
        for field in ['rawHeightInches', 'rawWeightLb']:
            valid = [(p, q) for p, q in pairs if p[field] is not None and q[field] is not None]
            changed = [{'id': p['playerId'], 'name': q['name'], 'before': p[field], 'after': q[field],
                        'difference': q[field] - p[field]} for p, q in valid if p[field] != q[field]]
            changes[field] = {'matchedObservedPlayers': len(valid), 'changedPlayers': len(changed),
                              'changedList': changed, 'note': 'Metadata changes do not identify physical growth, training or measurement methodology.'}
        transitions.append({'from': a, 'to': b, 'changes': changes})
    result = {'generatedAt': datetime.now(timezone.utc).isoformat(), 'protocolSHA256': expected,
              'scope': protocol['scope'], 'localCandidateInventory': inventory,
              'deployedCardFields': all_fields, 'seasons': reports, 'adjacentSeasonMetadata': transitions,
              'noOutcomeAnalysis': True, 'noImputation': True}
    dump(HERE / 'analysis.json', result)
    dump(HERE / 'body-records.json', records)
    print(json.dumps({'seasons': [{k: r[k] for k in ['season', 'players', 'rotationPlayers', 'coverage', 'missingRawBody',
                                                   'rankReconstructionMismatches', 'correlations']} for r in reports],
                      'inventoryFiles': len(inventory)}, ensure_ascii=False))


if __name__ == '__main__':
    run()
