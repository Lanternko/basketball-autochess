import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SEASONS = ['2022-23', '2023-24', '2024-25', '2025-26']

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    assert not (HERE / 'protocol.json').exists(), 'Never overwrite a registration'
    old = sorted({p for scope in ['src', 'scripts', 'reports/defense-tenth']
                  for p in (ROOT / scope).rglob('*') if p.is_file() and HERE not in p.parents})
    dump(HERE / 'protected-before.json', {p.relative_to(ROOT).as_posix(): sha(p) for p in old})
    inputs = []
    for s in SEASONS:
        inputs += [(ROOT / 'data/season-source/player-games.json' if s == '2025-26'
                    else ROOT / f'data/defense-seventh/{s}/player-games.json'),
                   ROOT / 'data/benchmark-source/bio.json' if s == '2025-26'
                   else ROOT / f'data/defense-seventh/{s}/bio.json',
                   ROOT / f'reports/defense-tenth/step4-t2/raw/{s}/0-advanced.json']
    protocol = {
        'version': 'oreb-talent-increment-1', 'registeredAt': datetime.now(timezone.utc).isoformat(),
        'goal': 'Incremental out-of-sample prediction beyond own prior rebounding rates. Explanation alone is not adoption. No cards, engine edits, simulation or next-layer mechanisms.',
        'label': '四季均已看過答案；回溯資料外診斷，不是新盲測。體測發生年份可核對，歷史發布快照無法保證。',
        'seasons': SEASONS,
        'acquisition': {'combineYears': list(range(2000, 2026)),
            'endpoints': ['draftcombineplayeranthro', 'draftcombinedrillresults'],
            'combineParams': 'LeagueID=00, SeasonYear=integer calendar year',
            'tracking': ['Rebounding', 'SpeedDistance'], 'trackingSeasons': SEASONS,
            'source': 'Official NBA stats API. No name-based/fuzzy IDs, no fabricated values. Public raw mirror permitted only if explicitly documented; mirror-only data remain exploratory and cannot confirm a predictive gain.',
            'concurrency': 4, 'timeoutMS': 15000, 'attempts': 2,
            'emptyResponse': 'Record valid empty rows as empty, not zero coverage of NBA players. Failed requests recorded and not silently dropped.'},
        'features': {'static': ['origin-season recorded height', 'origin-season recorded mass', 'combine wingspan', 'combine standing reach'],
            'athletic': ['standing vertical', 'maximum vertical', 'bench press repetitions', 'lane agility time', 'modified lane agility time', 'three-quarter sprint time', 'years since combine'],
            'behaviorSeparate': ['origin offensive average speed', 'origin defensive average speed', 'origin offensive rebound chances per36', 'origin contested offensive rebound fraction'],
            'timeRule': 'Latest available nonmissing NBA-ID-matched combine observation per field with combine year <= origin-season starting year. Never use a target-season performance or target-season body field as a cross-season predictor. Full-season tracking only used as an origin-season predictor for next season, never an early-season predictor of its own later games.',
            'zeroRule': 'Bench repetitions0 is observed0 if explicitly numeric; other body/test quantities must be positive finite. Store missing flags and dates. No strength rating is inferred from mass/OREB/BLK.',
            'forbidden': ['team/player identity as features', 'team net/wins/rank', 'stint/on-off outcomes', 'target-season rates as inputs', 'draft selection or country as talent proxy']},
        'association': 'Four separate seasons, >=500MIN, individual OREB% and OREB/36 versus each observed body/test variable. Pearson/Spearman and n. Descriptive association only, not causal coefficients; no fishing-based feature selection.',
        'prediction': {
            'crossSeasonMain': 'Fit2022-23->2023-24 and2023-24->2024-25; evaluate2024-25->2025-26 once. Both source/target MIN>=100. Outcomes next-season OREB/36 and official OREB_PCT (percentage points). Source MIN<500 and main-team-change groups reported separately; >=500 both seasons sensitivity.',
            'withinSeason': 'First20 and first41 positive-minute appearances versus remaining appearances; both portions >=100MIN. Evaluate2023-24 using2022-23 training;2024-25 using2022-23+2023-24;2025-26 using all earlier seasons. Outcome later OREB/36; no full-season advanced/tracking inputs in this task.',
            'mainTeamChange': 'Source vs target team with greatest observed minutes differs. Grouping only, never a predictor. This is a portability stress test, not a causal trade effect.',
            'models': {
                'persistence': 'Raw source outcome rate; no fitted slope. For OREB% forecast, source official OREB%.',
                'orebPctOnly': 'Cross-season: own source official OREB% and log1p(source MIN). Within-season: own early OREB/36 and log1p(early MIN).',
                'history': 'Own source outcome rate, log1p(source MIN), plus official source OREB% for cross-season OREB/36 outcome. This stronger baseline prevents claiming gain over a weak OREB%-only comparison.',
                'static': 'history + static dimensions',
                'talent': 'history + static dimensions + athletic tests',
                'talentOnly': 'Static + athletic tests + log1p(source MIN); no own rebound history. Diagnostic of explanation and missing/low-sample cases.',
                'missingOnly': 'history + availability flags and years since combine only; negative control for test participation/selection.',
                'behavior': 'talent + behaviorSeparate, cross-season only; must not be described as intrinsic talent.'},
            'estimator': 'Linear ridge; training-only median imputation plus missingness indicators and standardization. All-missing training columns neutral0 with indicator. Intercept unpenalized. Training weight=min(target MIN,1000); prediction lower clipped0, OREB% capped100; no post-result tuning.',
            'ridge': {'grid': [.1, 1, 10, 100, 1000], 'folds': 5,
                'groupRule': 'SHA256 of string playerID modulo5, same player stays in same fold across seasons. Select minimum weighted validation MSE; tie choose larger ridge. Training data only.'},
            'metrics': 'Target-minute-weighted MAE/RMSE for rates; Pearson. Also mean absolute player season-count error using given true target MIN, explicitly conditional exposure, not forecasting minutes. OREB% is a share and is not itself an absolute count.',
            'uncertainty': {'replicates': 20000, 'seed': 20261055,
                'scheme': 'Paired target-franchise resampling crossed with player Poisson weights, player/franchise weights matched across seasons and versions. No simulation seeds exist in this offline analysis. This does not replace franchise+simulation-seed acceptance required for future engine adoption; training refit uncertainty excluded.'},
            'interpretation': 'Confirm only incremental predictive gain against history with a wholly negative paired95 interval. Individual features/within-season/small-sample/mover groups exploratory; no multiplicity-free significance claim. Four seasons already seen; no engine adoption in this batch.'},
        'failureRules': 'Report fetch/schema/ID/coverage failures, complete-case selection and old-test age. If data unavailable, report unavailable rather than manufacture skill or assert no relationship. No post-result feature selection or change to tests.',
        'expected': 'Physical measurements may help low-sample priors or role transfer; no numerical gain promised. Role/context may dominate and existing OREB% may already subsume physical advantages.',
        'inputHashes': {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
        'protectedManifestSHA256': sha(HERE / 'protected-before.json'),
        'registrationCodeSHA256': sha(Path(__file__))}
    dump(HERE / 'protocol.json', protocol)
    digest = sha(HERE / 'protocol.json')
    (HERE / 'protocol.sha256').write_text(digest + '  protocol.json\n', encoding='utf-8')
    print(json.dumps({'registeredAt': protocol['registeredAt'], 'sha256': digest, 'protected': len(old)}))
