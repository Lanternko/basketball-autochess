"""Register the body-input audit before generating any coverage/statistical output."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SEASONS = ['2022-23', '2023-24', '2024-25', '2025-26']

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    if (HERE / 'protocol.json').exists():
        raise RuntimeError('Already registered; do not overwrite')
    protected = sorted({p for folder in ['src', 'scripts', 'reports/defense-tenth']
                        for p in (ROOT / folder).rglob('*') if p.is_file() and HERE not in p.parents})
    snapshot = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
    dump(HERE / 'protected-before.json', snapshot)
    inputs = []
    for season in SEASONS:
        folder = ROOT / 'data/defense-seventh' / season
        inputs.extend([ROOT / f'reports/defense-tenth/step4-t0/{season}/bundle.json',
                       (ROOT / 'data/season-source/player-games.json' if season == '2025-26'
                        else folder / 'player-games.json'),
                       ROOT / 'data/benchmark-source/bio.json' if season == '2025-26' else folder / 'bio.json'])
        if season != '2025-26':
            inputs.append(folder / 'league.json')
    inputs.extend(ROOT / p for p in ['scripts/build_season_league.js',
                                    'scripts/fetch_defense_seventh_season.js',
                                    'reports/defense-tenth/step4-t0/prepare.mjs',
                                    'src/rebound_block_model.js', 'src/probability_model.js',
                                    'src/defense_fourth_game.js', 'src/constants.js'])
    rules = {
        'version': 'body-input-audit-1',
        'registeredAt': datetime.now(timezone.utc).isoformat(),
        'scope': 'Layer 1 only: existing height/mass/strength/jump inputs and old physique mapping. No cards, engine edits, simulation, parameter fitting or new player-data downloads. Stop after report.',
        'seasons': SEASONS,
        'label': '四季均已看過答案；資料與表示法稽核，不是預測／籃板成績檢定',
        'cohort': 'Unique individual PLAYER_ID per season from official player-games, positive summed MIN. Report zero-minute IDs separately. Aggregate traded-player minutes once across teams. Rotation subcohort GP>=30 and MIN/GP>=20.',
        'coverage': 'For each component report observed positive finite value count and minute-weighted coverage; strict seasonal raw bio is distinct from deployed card fields/defaults. Never label default79in/210lb as observed. Record raw/card discrepancies and duplicate-card conflicts.',
        'components': {
            'size': ['height', 'wingspan', 'standing reach'],
            'mass': ['weight'],
            'strength': ['bench press or other independently measured strength; never inferred from body mass/REB/BLK'],
            'jump': ['standing and maximum vertical leap; draft-date measurement is not current-season jump'],
            'stamina': 'Separate existing attribute, not an observed strength/jump measurement. Audit recipe only.'},
        'localInventory': 'Search data/ and reports/ filenames for bio/combine/anthro/measurement/player-info/commonplayer/draft/physical and inspect known seasonal raw bio and deployed bundles. List paths and schemas. Do not infer a measurement exists from generated report text; explicitly state search scope.',
        'statistics': 'Descriptive only: population Pearson/Spearman of raw height, mass, height+mass/10 and deployed physique; exact legacy rank reconstruction; raw source vs deployed mismatch lists; adjacent-season raw changes and source availability timestamps. No OREB/DREB/PPP/net/wins correlations or optimization. No causal strength conclusion.',
        'missingness': 'Null is missing, numeric zero and nonfinite are invalid for body quantities; preserve raw strings. No imputation; missing flag and provenance required. Proposed missingness rules do not create cards.',
        'representation': 'Propose separate physical-units fields with source, measurement date, availability date, uncertainty and missingness; no new 0-120 scalar. Derived standing reach plus jump only if both observed, with no repeated height/wingspan bonus. No fitted coefficients.',
        'acceptance': 'Completeness/provenance and reproducibility only. No claims of rebound/team accuracy improvement, no adoption change. Layer2+ deferred.',
        'protectedManifestSHA256': sha(HERE / 'protected-before.json'),
        'inputHashes': {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
        'registrationCodeSHA256': sha(Path(__file__))}
    dump(HERE / 'protocol.json', rules)
    digest = sha(HERE / 'protocol.json')
    (HERE / 'protocol.sha256').write_text(digest + '  protocol.json\n', encoding='utf-8')
    print(json.dumps({'registeredAt': rules['registeredAt'], 'sha256': digest,
                      'protectedFiles': len(snapshot), 'inputs': len(inputs)}))
