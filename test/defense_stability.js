import assert from 'node:assert/strict';
import {read,hash} from '../scripts/defense_io.js';
import {NBA_DEFENSE_V1} from '../src/defense_presets.js';
import {DEFENSE_STATS} from '../src/defense_validation.js';

const verify=manifest=>{
  for(const [file,expected] of Object.entries(manifest))assert.equal(hash(file),expected,'Stale artifact dependency: '+file);
};
const near=(a,b,label)=>assert.ok(Math.abs(a-b)<.02,label+': '+a+' versus '+b);
const report=read('reports/defense-stability.json');
verify(report.provenance.code);verify(report.provenance.sources);
const calibration=read('reports/defense-calibration.json');
verify(calibration.provenance.code);verify(calibration.provenance.sources);
for(const [key,value] of Object.entries(calibration.selected))assert.equal(NBA_DEFENSE_V1[key],value);
assert.equal(report.runs.length,12);
assert.equal(new Set(report.runs.map(r=>r.seed)).size,4);
const fixtureIds=read('data/season-league.json').schedule.map(g=>g.id);
for(const seed of new Set(report.runs.map(r=>r.seed))){
  const rows=report.runs.filter(r=>r.seed===seed);
  assert.deepEqual(rows.map(r=>r.id).sort(),['control','corrected','reference']);
  const reference=rows.find(r=>r.id==='reference'),corrected=rows.find(r=>r.id==='corrected');
  const {foulConditioning:oldCondition,...oldOptions}=reference.options;
  const {foulConditioning:newCondition,...newOptions}=corrected.options;
  assert.equal(oldCondition,false);assert.equal(newCondition,true);
  assert.deepEqual(oldOptions,newOptions,'Paired conditions must differ only in foul sampling');
  assert.ok(Math.abs(corrected.summary.global.fg-report.target.fg)<Math.abs(reference.summary.global.fg-report.target.fg));
  assert.ok(corrected.summary.defensiveRatingMAE<reference.summary.defensiveRatingMAE);
  assert.equal(hash(corrected.artifact.file),corrected.artifact.sha256);
  const season=read(corrected.artifact.file);
  verify(season.provenance.code);verify(season.provenance.sources);
  assert.deepEqual(season.summary,corrected.summary);
  assert.equal(season.seed,seed);assert.equal(season.options.minuteMode,'heuristic');
  assert.equal(season.options.foulOut??6,6);
  for(const [key,value] of Object.entries(NBA_DEFENSE_V1))assert.equal(season.options[key],value);
  assert.deepEqual(season.matches.map(g=>g.id),fixtureIds);
  assert.equal(season.accounting.length,30);
  assert.equal(season.accounting.reduce((sum,t)=>sum+t.wins,0),1230);
  for(const t of season.accounting){
    const games=season.matches.filter(g=>g.homeId===t.id||g.awayId===t.id);
    assert.equal(games.length,82);assert.equal(t.games,82);
    const points=games.reduce((sum,g)=>sum+(g.homeId===t.id?g.scoreA:g.scoreB),0);
    const against=games.reduce((sum,g)=>sum+(g.homeId===t.id?g.scoreB:g.scoreA),0);
    assert.equal(t.stats.pts,points);assert.equal(t.opponent.pts,against);
    assert.equal(t.players.reduce((sum,p)=>sum+p.plusMinus,0),5*(points-against));
    for(const key of DEFENSE_STATS.filter(k=>k!=='poss'))near(t.players.reduce((sum,p)=>sum+p.stats[key],0),t.stats[key],t.name+' '+key);
    near(t.stats.regulationSeconds,82*5*2880,t.name+' regulation seconds');
    near(t.stats.seconds,5*(82*2880+t.overtimes*300),t.name+' total seconds');
    assert.equal(t.stats.liveTov+t.stats.deadTov,t.stats.tov);
    assert.equal(t.stats.liveTov,t.opponent.stl);
    assert.equal(t.stats.tov,t.stats.clockTov+t.stats.touchTov+t.opponent.passSteals);
    assert.equal(t.stats.stl,t.stats.passSteals+t.stats.touchSteals);
    assert.equal(t.stats.fga,t.stats.fg3a+t.stats.mida+t.stats.rima);
    assert.equal(t.stats.fgm,t.stats.fg3m+t.stats.midm+t.stats.rimm);
    assert.ok(t.stats.blk<=t.opponent.fga-t.opponent.fgm);
  }
}
console.log('PASS four complete season artifacts, paired correction stability, score/minute/turnover/plus-minus conservation and dependency fingerprints');
