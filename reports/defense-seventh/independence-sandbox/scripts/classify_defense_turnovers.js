import fs from 'node:fs';
import {read,hash} from './defense_io.js';
const source=read('data/defense-a-source/manifest.json'),groups={},liveTypes={},rawTypes={};
for(const s of source.sources){if(hash(s.file)!==s.sha256)throw Error('Stale PBP');for(const e of read(s.file).data.game.actions){if(e.actionType!=='turnover')continue;
  const type=e.subType??'unknown',descriptor=(e.descriptor??'').toLowerCase(),live=e.stealPersonId>0;
  const group=type==='shot clock'?'shotClock':type==='offensive foul'?'offensiveFoul':type==='bad pass'||type==='inbound'||type==='out-of-bounds'&&descriptor==='bad pass'?'passing':type==='lost ball'||type==='out-of-bounds'&&descriptor==='lost ball'?'handling':type==='out-of-bounds'?'outOfBoundsUnclassified':'otherViolation';
  if(!groups[group])groups[group]={count:0,live:0,dead:0};groups[group].count++;groups[group][live?'live':'dead']++;
  rawTypes[type]=(rawTypes[type]??0)+1;if(live)liveTypes[type]=(liveTypes[type]??0)+1;
}}
const n=Object.values(groups).reduce((n,g)=>n+g.count,0);for(const g of Object.values(groups)){g.perTeamGame=g.count/(2*source.sources.length);g.share=g.count/n;g.livePerTeamGame=g.live/(2*source.sources.length);}
const result={games:source.sources.length,turnovers:n,groups,rawTypes,liveTypes,definitions:'Live = official turnover has stealPersonId. Passing includes bad pass, inbound and out-of-bounds descriptor bad pass; handling includes lost ball and out-of-bounds descriptor lost ball. Unknown retained explicitly. Simulator pass interceptions and touch live turnovers can be compared with these live categories; generic dead touch turnovers cannot be resolved into passing/handling/fouls without a new engine mechanism.',provenance:{manifest:hash('data/defense-a-source/manifest.json'),code:hash('scripts/classify_defense_turnovers.js')}};
fs.writeFileSync('reports/defense-b1/turnover-types.json',JSON.stringify(result,null,2)+'\n');console.log(groups);
