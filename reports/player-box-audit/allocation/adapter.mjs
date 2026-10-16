import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const cache=new Map();
export async function candidateSeason(version){
 if(cache.has(version))return cache.get(version);
 if(!['dreb-allocation','block-allocation','box-allocation'].includes(version))throw Error('Unknown intervention');
 let source=fs.readFileSync('reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs','utf8');
 const edits=[];
 if(version!=='block-allocation')edits.push(`
 const fromReb="reboundWeights(ls[side],{zone,side:offensive?'offense':'defense',shooterIndex:offensive?slot:-1,freeThrow},opt)";
 if(g.split(fromReb).length!==2)throw Error('Defensive rebound allocation anchor');
 g=g.replace(fromReb,"(offensive?reboundWeights(ls[side],{zone,side:'offense',shooterIndex:slot,freeThrow},opt):measuredRecipientWeights(ls[side],'dreb'))");
 `);
 if(version!=='dreb-allocation')edits.push(`
 const fromBlk="blocker=D.lineup[pickWeighted(bp.weights,rng())]";
 if(g.split(fromBlk).length!==2)throw Error('Block allocation anchor');
 g=g.replace(fromBlk,"blocker=D.lineup[pickWeighted(measuredRecipientWeights(ls[1-off],'blk'),rng())]");
 `);
 const moduleUrl=pathToFileURL(path.resolve('src/individual_box_allocation.js')).href;
 edits.push(`g="import {measuredRecipientWeights} from '${moduleUrl}';\\n"+g;`);
 const anchor='  const gu=encode(g),s=';if(source.split(anchor).length!==2)throw Error('Adapter anchor');
 source=source.replace(anchor,edits.join('\n')+'\n'+anchor);
 const mod=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
 const run=await mod.experimentalSeason();cache.set(version,run);return run;
}
