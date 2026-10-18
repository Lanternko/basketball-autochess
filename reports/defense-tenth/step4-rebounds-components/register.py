"""Preregister separated offensive rebound opportunity/conversion tests."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SEASONS = ['2022-23','2023-24','2024-25','2025-26']

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def dump(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    assert not (HERE/'protocol.json').exists(),'Never replace a registration'
    protected=sorted(f for scope in ['src','scripts','reports/defense-tenth']
                     for f in (ROOT/scope).rglob('*') if f.is_file() and HERE not in f.parents)
    dump(HERE/'protected-before.json',{f.relative_to(ROOT).as_posix():sha(f) for f in protected})
    inputs=['reports/defense-tenth/step4-rebounds-talent/features.json',
            'reports/defense-tenth/step4-rebounds-talent/results.json',
            'reports/defense-tenth/step4-rebounds-talent/protocol.json',
            'reports/defense-tenth/step4-rebounds-talent/completion-audit.json']
    inputs += [f'reports/defense-tenth/step4-rebounds-talent/raw/tracking/{s}-Rebounding.json' for s in SEASONS]
    p={
      'version':'oreb-components-offline-1','registeredAt':datetime.now(timezone.utc).isoformat(),
      'scope':'Separated incremental forecasting tests only. No new acquisition, cards, engine, simulations or coefficient adoption. Complete this batch and stop.',
      'label':'四季已看過答案；回溯的時間資料外診斷，不是新盲測。',
      'seasons':SEASONS,
      'timeSplits':{
        'primary':'Train2022-23->2023-24 and2023-24->2024-25; test2024-25->2025-26.',
        'replication':'Train2022-23->2023-24; test2023-24->2024-25.',
        '2023-24':'No fitted evaluation: no earlier training pair available. Descriptive component stability only.',
        'cutoff':'Every predictor from the source season, never target-season tracking/rates/role/minutes. Known target MIN used only as evaluation weight/count exposure, never a predictor.'},
      'cohort':'Same as prior talent study: source and target observed MIN>=100, valid source official OREB%, valid target outcome; target rate and OREB% in separate tasks. No deletion based on tracking availability. Missing indicators and train-only imputation. Rookie/no-history players not included.',
      'features':{
        'chance':'Source tracking OREB_CHANCES / source tracking MIN *36, a realized tracking opportunity rate, not starting location.',
        'conversion':'Source tracking OREB / OREB_CHANCES, if denominator>0 and numerator in[0,denominator]; otherwise missing and audited.',
        'adjustedConversion':'Source OREB/(OREB_CHANCES-OREB_CHANCE_DEFER), if denominator>0 and valid; exploratory only. Do not call deferrals box-out assists.',
        'history':'Source individual box OREB/36, official OREB% and log1p(MIN); OREB% outcome omits source OREB/36 to match previous baseline.',
        'missingControl':'History plus flags for missing chance and raw conversion only; no availability count containing hidden chance information.',
        'forbidden':['player/team identity as features','target-season predictor','team net/wins/rank','stint/on-off','height,athletic tests,speed,contested share','AVG_OREB_DIST as pre-shot distance','position-specific fixed crash bonus']},
      'models':{
        'persistence':'Raw source box OREB/36 for rate, raw source official OREB% for pct.',
        'pctOnly':'Source official OREB% and log1p(MIN).',
        'history':'Unchanged prior talent-study history recipe.',
        'chance':'history + source chance only.',
        'conversion':'history + source raw conversion only.',
        'both':'history + chance + raw conversion.',
        'adjustedBoth':'history + chance + adjusted conversion; exploratory.',
        'missingOnly':'history + chance/conversion missing indicators; negative control.'},
      'estimator':{
        'type':'Linear ridge with unpenalized intercept, training-only median imputation, missing indicators and standardization. Same numeric procedure as prior study.',
        'grid':[0.1,1,10,100,1000],'folds':5,
        'foldRule':'SHA256(string playerID) modulo5; same person in same fold across all training years. Min weighted CV MSE, larger lambda on exact tie.',
        'trainWeight':'min(target MIN,1000), normalized mean1; all training targets precede source-season end of test.',
        'predictionClip':'rate>=0, OREB% in[0,100] percentage points. No test-season scaling or tuning.'},
      'metrics':{
        'rate':'Target-minute-weighted MAE/RMSE of individual OREB/36; Pearson.',
        'pct':'Target-minute-weighted MAE/RMSE of official individual OREB%, percentage points; Pearson.',
        'conditionalCount':'Mean abs(rate prediction * given target MIN/36 - actual OREB); true exposure diagnostic, not minutes forecasting.',
        'pool':'Two forward-tested target seasons; equal season weights after within-season target-minute weighting. Pooled RMSE=sqrt(mean season MSE); pooled countMAE=mean season countMAE. Not a team-season game metric.'},
      'groups':{'all':'Main cohort','movers':'Different main team (maximum observed MIN) source vs target; grouping only, not causal trade estimate.',
                'stayers':'Same main team','lowSourceMinutes':'100<=source MIN<500','both500':'Both seasons MIN>=500. Groups with fewer than10 observations not estimated.'},
      'uncertainty':{
        'replicates':20000,'seed':20261056,
        'scheme':'Paired franchise resampling crossed with player Poisson1 weights; common player/franchise weights across target seasons and all models. Equal-season normalization within each replicate. No simulation seeds exist; not engine adoption uncertainty. Training refit uncertainty excluded.',
        'levels':[0.95,1-0.05/6],
        'primaryFamily':'Six primary rate-MAE comparisons: chance/conversion/both against each of persistence/history in 2025-26 all-player cohort. Bonferroni99.1667% intervals alongside95%. Other targets/seasons/groups exploratory.',
        'jointLabel':'球隊＋球員聯合重抽；不是球隊＋模擬seed。'},
      'decision':{
        'supportedIncrement':'Development-data candidate only if primary2025 rate MAE Bonferroni interval wholly negative against BOTH persistence and history, rate RMSE not significantly worse at95%; and2024 replication and movers show no significant MAE deterioration at95%. Does not authorize engine adoption.',
        'failure':'If no primary candidate passes, report no verifiable incremental predictive value in current features. Do not choose adjustedBoth or a subgroup post hoc to evade this rule.',
        'noCausalClaim':'Chance may encode role/environment and overlaps realized rebounds; good forecast does not identify box-out or participation causal coefficient.'},
      'descriptiveChecks':[
        'Exact OREB/36 from same tracking sample = chance36 * raw conversion where denominator positive; not additional information.',
        'Reported raw/adjusted percentages versus count ratios: allow0.000501 rounding, list mismatches; never silently change raw records.',
        'Missing/negative/invalid counts, duplicate IDs, tracked-minute coverage and per-model same cohort.',
        'Three adjacent-pair opportunity/conversion/rate/PCT Pearson stability, including movers; >=500MIN sensitivity.',
        'Track-vs-box OREB counts and MIN differences; no mixing denominators or asserting count identity across samples.'
      ],
      'inputHashes':{f:sha(ROOT/f) for f in inputs},
      'protectedManifestSHA256':sha(HERE/'protected-before.json'),
      'registrationCodeSHA256':sha(Path(__file__))}
    dump(HERE/'protocol.json',p)
    (HERE/'protocol.sha256').write_text(sha(HERE/'protocol.json')+'  protocol.json\n',encoding='utf-8')
    print(json.dumps({'at':p['registeredAt'],'sha256':sha(HERE/'protocol.json'),'protectedFiles':len(protected)}))
