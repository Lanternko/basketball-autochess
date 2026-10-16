"""Register the opportunity/role/helper diagnostic before any results."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SEASONS = ['2022-23', '2023-24', '2024-25', '2025-26']

def sha(f):
    h = hashlib.sha256()
    with Path(f).open('rb') as stream:
        for b in iter(lambda: stream.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def dump(f, obj):
    Path(f).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

if __name__ == '__main__':
    assert not (HERE/'protocol.json').exists(), 'Never overwrite registration'
    old = sorted(f for scope in ['src', 'scripts', 'reports/defense-tenth']
                 for f in (ROOT/scope).rglob('*') if f.is_file() and HERE not in f.parents)
    dump(HERE/'protected-before.json', {f.relative_to(ROOT).as_posix():sha(f) for f in old})
    inputs = ['src/rebound_block_model.js', 'src/defense_fourth_game.js', 'src/rng.js',
              'src/minute_budget.js', 'src/probability_model.js', 'src/defense_fourth_effects.js',
              'src/constants.js', 'src/defense_probability.js', 'src/court-scene.js',
              'reports/defense-tenth/step4-rebounds/model.mjs']
    for s in SEASONS:
        inputs += [f'reports/defense-tenth/step4-t0/{s}/bundle.json',
                   f'reports/defense-tenth/step4-t2/raw/{s}/0-advanced.json',
                   f'reports/defense-tenth/step4-t2/raw/{s}/0-hustle.json']
    p = {
        'version':'rebound-opportunity-audit-1', 'at':datetime.now(timezone.utc).isoformat(),
        'scope':'Diagnostic only: conservation, competition, role labels, missing helper/space paths. No new mechanism, card, coefficient, season simulation or downloads. Finish this item and stop.',
        'label':'Four seasons already seen; synthetic probes reveal model behavior, not real causal effects or accuracy gains.',
        'seasons':SEASONS, 'seeds':list(range(20261012,20261032)),
        'opportunitiesPerSeed':10000,
        'kernel':{
            'input':'Frozen pure v3 FG rebound kernel, five stint signals off/no map. No team/FT/period-expiry branch in kernel probe; actual game audit checks these separately.',
            'neutral':'PG,SG,SF,PF,C, all rebound=physique=70. Synthetic modifications use rebound99, physique unchanged, unless anchor explicitly physique90.',
            'exposure':'Equal weights over short/mid/long misses and five shooter indices, independent of cards. Designed exposure, not estimated NBA frequencies.',
            'talentStack':'k=0..5 strong rebounders. Average exact probabilities across every subset of k slots to avoid choosing favorable positions. 30% uniform luck and existing 5%-60% team probability clamp preserved.',
            'realTop5':'Per season deduplicate by playerId using card with largest observed in-team MIN, sum observed MIN across teams for >=1000MIN eligibility. Select top5 official OREB_PCT, tie lower playerId. Use unchanged v3 attributes and nominal court positions, not OREB_PCT as a new probability input.',
            'role':'Neutral teammates, anchor index4 rebound99/physique90. Baseline C; change pos only with courtPosition=C; change courtPosition only to PG; swap PG/C courtPosition to retain balanced labels. Actual attributes/physical traits unchanged. Report per-zone nonshooter and anchor-shooter effects plus exposure-average team/player probability. Defensive-side effects separately.',
            'ignoredInputs':'Add boxOut=99,boxOutHelp=99 to anchor; independently add reboundStartDistanceFeet=0 vs30 to all players, crashIntent=0 vs1. Compare full output probabilities exactly; these are hypothetical metadata probes, not new observed skills.',
            'sampling':'Each seed draws 10000 zone/shooter/side/recipient uniforms, shared across scenarios. One Bernoulli team decision then one categorical recipient. Save seed means and SE; exact probabilities are primary.'},
        'actualGameAudit':{
            'cases':['neutral','allStrong','anchorC','anchorPG','anchorPosOnlyPG','boxOutHigh','distanceFar'],
            'games':'20 seeds per case, 140 games. Five-player synthetic teams against neutral; full frozen 2025-26 v3 timing/accounting constants, five signals off, defenseSignals deleted, no substitutions/fatigue/rotation/minute targets; foulOut99. This controls exposure, not realistic rotations.',
            'ledger':'For each completed opportunity: sum player OREB+DREB+teamOreb+teamDreb across sides equals reboundChances. Replay must have one terminal rebound per preceding FGX/final nontechnical FTX; nonfinal FT dead rebounds separate; expiry can leave a miss unresolved. More than one OREB in poss allowed only following another miss.',
            'parity':'boxOutHigh and distanceFar must match neutral exactly in scores, full team/player stats and events if inputs are unused; anchorPosOnlyPG kernel parity required, full-game differences if other paths consume pos must be reported without attributing them to rebounding.',
            'accuracy':'No win/net MAE or adoption claim from synthetic games; no new constants calibrated.'},
        'hustle':{
            'input':'Existing league-wide Totals hustle tables only, no new acquisition.',
            'summary':'BOX_OUT_PLAYER_TEAM_REBS minus BOX_OUT_PLAYER_REBS; OFF_BOXOUTS and DEF_BOXOUTS separately. Raw player-credited records, not unique team possessions. No offensive/defensive recovery split invented; do not infer causal extra boards or convert into additive board counts.',
            'validity':'Report invalid negative differences or team recovery>boxouts; never silently force counts to fit.'},
        'rules':{'conservationTolerance':1e-12,
                 'missingMechanism':'Zero exact response to a hypothetical field documents absence, not evidence that real boxing-out or distance has no effect.',
                 'uncertainty':'Kernel seed SE/t19 interval measures Monte Carlo error only, not franchise generalization or real causal effect. No franchise+seed adoption comparison in this item.',
                 'proposal':'Write a chronological next-mechanism specification, measurable labels, unidentifiable effects, no fabricated fitted constants. Do not implement it in this diagnostic.'},
        'inputHashes':{f:sha(ROOT/f) for f in inputs},
        'protectedManifestSHA256':sha(HERE/'protected-before.json'),
        'registrationCodeSHA256':sha(Path(__file__))}
    dump(HERE/'protocol.json',p)
    (HERE/'protocol.sha256').write_text(sha(HERE/'protocol.json')+'  protocol.json\n',encoding='utf-8')
    print(json.dumps({'at':p['at'],'sha256':sha(HERE/'protocol.json'),'protectedFiles':len(old)}))
