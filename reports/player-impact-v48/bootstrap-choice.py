from pathlib import Path
R=Path('reports/player-impact-v48');P=Path('reports/player-impact-v47')
w=(P/'worker.mjs').read_text(encoding='utf-8').replace("from './input.mjs'","from './choice-input.mjs'").replace("from './engine.mjs'","from './choice-engine.mjs'")
w=w.replace("parentPort.on('message'", "import {offenseCollector} from './offense-collector.mjs';\nparentPort.on('message'")
w=w.replace('fine=fineCollector(job.seed^0x45F1A);','fine=fineCollector(job.seed^0x45F1A),offense=offenseCollector(job.seed^0x45F1A);').replace('fine.event(e);','fine.event(e);offense.event(e);').replace('r.fineDefense=fine.finish(r.teams);','r.fineDefense=fine.finish(r.teams);r.fineOffense=offense.finish(r.teams);assert.deepEqual(r.fineOffense.total,r.fineDefense.total);')
(R/'worker.mjs').write_text(w,encoding='utf-8')
s=(P/'run.mjs').read_text(encoding='utf-8').replace("root='reports/player-impact-v47'","root='reports/player-impact-v48'").replace("variant='v47'","variant='v48'").replace("protocol=read(root+'/protocol.json')","protocol=read(root+'/choice-protocol.json')")
start=s.index('const files=');end=s.index('\nconst hashes=',start);s=s[:start]+"const files=['choice-protocol.json','worker.mjs','choice-input.mjs','run.mjs','engine.mjs','choice-engine.mjs','choice-model.mjs','fit.py','fit-choice.py','choice-fit.json','choice-selection.json','choice-verify.mjs','offense-collector.mjs'];"+s[end:]
start=s.index('const hashes=');end=s.index('\nconst verify=',start);s=s[:start]+"const hashes={...read('reports/player-impact-v47/candidate-run-protocol.json').hashes,...Object.fromEntries(files.map(f=>[root+'/'+f,hash(root+'/'+f)]))};"+s[end:]
(R/'run.mjs').write_text(s,encoding='utf-8')
for name in ['score.py','score-fine.py']:
 s=(P/name).read_text(encoding='utf-8').replace('v47','__NEW__').replace('v46','v47').replace('__NEW__','v48');(R/name).write_text(s,encoding='utf-8')
# Keep the original make-only prototype verification separately.
s=(R/'verify.mjs').read_text(encoding='utf-8').replace("from './input.mjs'","from './choice-input.mjs'").replace("from './engine.mjs'","from './choice-engine.mjs'").replace("import {offensiveMakePlan} from './model.mjs';","import {offensiveChoicePlan} from './choice-model.mjs';").replace('offensiveLineupMeasurement','offensiveChoiceMeasurement')
start=s.index("const os=b.league.teams[0].roster.slice(0,5)");end=s.index('\nconst run=await impactEngine',start)
s=s[:start]+"""const os=b.league.teams[0].roster.slice(0,5),p={finePlan:{zone:{ra:.2,paint:.2,mid:.2,corner:.1,arc:.3},makeEta:{ra:1,paint:2,mid:3,corner:4,arc:5}}},q=offensiveChoicePlan(p,os[0],os,false);
assert.equal(q.finePlan.zone.corner,p.finePlan.zone.corner);assert.equal(q.finePlan.zone.arc,p.finePlan.zone.arc);assert.deepEqual(q.finePlan.makeEta,p.finePlan.makeEta);assert.ok(Math.abs(q.finePlan.zone.ra+q.finePlan.zone.paint+q.finePlan.zone.mid-.6)<1e-12);assert.equal(offensiveChoicePlan(p,os[0],os,true),p);
for(const branch of ['paintGivenTwo','raGivenPaint']){const delta=os[0].offensiveChoiceMeasurement.shooterDelta[branch]+os.slice(1).reduce((s,p)=>s+p.offensiveChoiceMeasurement.teammateLogits[branch],0),actual=branch==='paintGivenTwo'?(q.finePlan.zone.ra+q.finePlan.zone.paint)/.6:q.finePlan.zone.ra/(q.finePlan.zone.ra+q.finePlan.zone.paint),old=branch==='paintGivenTwo'?2/3:.5;assert.ok(Math.abs(Math.log(actual/(1-actual))-Math.log(old/(1-old))-delta)<1e-12);}
"""+s[end:]
s=s.replace("'reports/player-impact-v48/verification.json'","'reports/player-impact-v48/choice-verification.json'")
(R/'choice-verify.mjs').write_text(s,encoding='utf-8')
print('created isolated choice candidate runtime and scorers')
