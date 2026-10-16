import fs from 'node:fs';
const cache=new Map();
export async function candidateSeason(version){
 if(cache.has(version))return cache.get(version);
 if(!['hazard-balance','creator-hazard','creator-only-hazard'].includes(version))throw Error('Unknown intervention');
 let source=fs.readFileSync('reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs','utf8');
 const initial=version==='creator-only-hazard'?'m.assists':version==='creator-hazard'?'m.attempts+.44*m.freeThrows+m.turnovers+m.assists':'m.attempts+.44*m.freeThrows+m.turnovers';
 const edits=`
 const fromHandler="volumeWeights(ls[off]):M.handlingWeights(ls[off])";
 if(g.split(fromHandler).length!==2)throw Error('Handler anchor');
 g=g.replace(fromHandler,"balancedTouchWeights(ls[off]):M.handlingWeights(ls[off])");
 const fromReceiver="volumeWeights(ls[off],'shot').map((w,i)=>i===hi?0:w)";
 if(g.split(fromReceiver).length!==2)throw Error('Receiver anchor');
 g=g.replace(fromReceiver,"volumeWeights(ls[off],'shot').map((w,i)=>i===hi?0:w/Math.max(.01,M.shootRate(Math.max(probability(i,assist).ev,probability(i).ev),passesLeft-1)))");
 const balanceAt="let p=best(hi,null), passesLeft=C.MAX_PASSES;";
 if(g.split(balanceAt).length!==2)throw Error('Initial probability anchor');
 // Initial shot-quality conditioning uses the same current lineup, defense,
 // forced=false state and no previous pass as the unchanged shot policy.
 const first="let hi=putback===null?pickWeighted";
 if(g.split(first).length!==2)throw Error('Initial declaration anchor');
 g=g.replace(first,"let hi=putback===null?pickWeighted");
 g+='\\nfunction balancedTouchWeights(lineup){return lineup.map(p=>{const m=p.offenseMeasurement;if(!(m?.minutes>0)||!(m.assists>=0))throw Error("Missing observations");return Math.max(.005,(${initial})/m.minutes);});}\\n';
 `;
 const anchor='  const gu=encode(g),s=';if(source.split(anchor).length!==2)throw Error('Adapter anchor');
 source=source.replace(anchor,edits+'\n'+anchor);
 const mod=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
 const run=await mod.experimentalSeason();cache.set(version,run);return run;
}
