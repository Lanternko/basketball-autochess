from pathlib import Path
R=Path('reports/player-impact-v40');old=Path('reports/player-impact-v30/model.mjs').read_text(encoding='utf-8');a="const source=link(fs.readFileSync('reports/player-impact-v28/model.mjs','utf8'),'reports/player-impact-v28/model.mjs',{'../../src/defense_probability.js':du});";assert old.count(a)==1
extra='''
let source=link(fs.readFileSync('reports/player-impact-v28/model.mjs','utf8'),'reports/player-impact-v28/model.mjs',{'../../src/defense_probability.js':du});
source=source.replace('export function exposureDefenseProbabilities(','export function legacyExposureDefenseProbabilities(');
source="import {sourceFreshDefense,shiftMakeLogit} from '"+url('src/source_fresh_defense.js')+"';\\n"+source+`
export function exposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup){
 const measured=lineup.filter(p=>p.freshDefenseMeasurement).length;
 if(opts.putback||measured===0)return legacyExposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup);
 if(measured!==5)throw Error('Partial source fresh defense lineup');
 const {logits,attributeDelta,sourcePhysique}=sourceFreshDefense(lineup);
 const neutral=baseProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,70,opts);
 const currentPhys=baseProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,phys,opts);
 const sourcePhys=baseProbability(handler,ctx,{...defender,onBall:70},70,oreb,dreb,sourcePhysique,opts);
 const q={...neutral,make:{...neutral.make}},shot=Math.max(0,1-q.pTovTouch-q.pFoul);
 for(const[z,m,x]of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){
  const limits=C.CLAMP['make'+z[0].toUpperCase()+z.slice(1)],value=shiftMakeLogit(neutral.make[z],logits[z])+attributeDelta[z]+currentPhys.make[z]-sourcePhys.make[z];
  q.make[z]=Math.max(limits[0],Math.min(limits[1],value));q[m]=shot*q.zone[z]*q.make[z];q[x]=shot*q.zone[z]*(1-q.make[z]);
 }
 q.ev=q.FG3M*3+(q.MIDM+q.RIMM)*2+q.pFoul*C.FT_ATTEMPTS*q.ftPct;return q;
}
`;
'''
(R/'model.mjs').write_text(old.replace(a,extra),encoding='utf-8')
engine=Path('reports/player-impact-v39/engine.mjs').read_text(encoding='utf-8');assert engine.count("url('reports/player-impact-v30/model.mjs')")==1;engine=engine.replace("url('reports/player-impact-v30/model.mjs')","url('reports/player-impact-v40/model.mjs')");(R/'engine.mjs').write_text(engine,encoding='utf-8')
text=Path('reports/player-impact-v30/prepare-contexts.mjs').read_text(encoding='utf-8').replace("const root='reports/player-impact-v30'","const root='reports/player-impact-v40'")
text=text.replace("import {loadInput} from '../player-impact-v20/role-input.mjs';","import {loadSourceInput as loadInput} from './input.mjs';")
text=text.replace("attachDefenseAnchors(b.league.teams.flatMap(t=>t.roster));attachCreationDependence(b.league.teams.flatMap(t=>t.roster));",'')
(R/'prepare-contexts.mjs').write_text(text,encoding='utf-8')
(R/'worker.mjs').write_text(Path('reports/player-impact-v39/worker.mjs').read_text(encoding='utf-8'),encoding='utf-8')
print('Isolated fresh-FG model and source centering scaffold prepared.')
