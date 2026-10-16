// Isolated probability fork: source role replaces FTR-derived creation
// dependence. Original probability source and all adopted imports stay intact.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href,encode=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const link=(s,file,map={})=>s.replace(/from\s+(['"])(\.\.?\/[^'"]+)\1/g,(_,q,f)=>`from ${q}${map[f]??url(path.resolve(path.dirname(file),f))}${q}`);
let probability=fs.readFileSync('src/probability_model.js','utf8').replaceAll('\r\n','\n');
const anchor='  const dependence = clamp(\n    C.CREATE_DEP_BASE + (M - selfCreation(handler)) / C.CREATE_DEP_SCALE, [0, 1]);';
if(probability.split(anchor).length!==2)throw Error('Creation dependence source anchor drift');
probability=probability.replace(anchor,'  const dependence = sourceCreationDependence(handler);');
probability=`import {creationDependence as sourceCreationDependence} from '${url('src/source_creation_dependence.js')}';\n`+link(probability,'src/probability_model.js');
const pu=encode(probability),defense=link(fs.readFileSync('src/defense_probability.js','utf8'),'src/defense_probability.js',{'./probability_model.js':pu}),du=encode(defense);

let source=link(fs.readFileSync('reports/player-impact-v28/model.mjs','utf8'),'reports/player-impact-v28/model.mjs',{'../../src/defense_probability.js':du});
source=source.replace('export function exposureDefenseProbabilities(','export function legacyExposureDefenseProbabilities(');
source="import {sourceFreshDefense,shiftMakeLogit} from '"+url('src/source_fresh_defense.js')+"';\n"+source+`
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

const model=await import(encode(source));
export const {contestDeltas,exposureDefenseProbabilities,terminalDefenseProbabilities}=model;
