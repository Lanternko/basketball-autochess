import fs from 'node:fs';import {classify} from './classify.mjs';
const root='reports/defense-tenth/step4-rebounds-after',p=JSON.parse(fs.readFileSync(root+'/protocol.json'));let out={};
const clock=e=>{const m=/PT(?:(\d+)M)?([\d.]+)S/.exec(e.clock??'');return m?60*Number(m[1]??0)+Number(m[2]):NaN;};
for(const season of p.seasons){const bundle=JSON.parse(fs.readFileSync(`reports/defense-tenth/step4-t0/${season}/bundle.json`)),folder=season==='2025-26'?'data/defense-a-source/pbp':`data/defense-seventh/${season}/pbp`;let games=[],missing=[],excluded={ft:0,team:0,invalidReference:0,invalidTime:0},failures=[];
for(const fixture of bundle.league.schedule){const id=fixture.id??fixture.gameId,file=folder+'/'+id+'.json';if(!fs.existsSync(file)){missing.push(id);continue;}try{const a=JSON.parse(fs.readFileSync(file)).data.game.actions,refs=new Map(a.map(x=>[x.actionNumber,x])),rows=[];
for(let i=0;i<a.length;i++){const e=a[i];if(e.actionType!=='rebound'||e.subType!=='offensive')continue;if(!e.personId||(e.qualifiers??[]).includes('team')){excluded.team++;continue;}const prev=refs.get(e.shotActionNumber);if(prev?.actionType==='freethrow'){excluded.ft++;continue;}if(!prev||!['2pt','3pt'].includes(prev.actionType)||prev.shotResult!=='Missed'||prev.teamId!==e.teamId||prev.period!==e.period){excluded.invalidReference++;continue;}
const reb={period:e.period,clock:clock(e),player:e.personId};let result={category:'unknown',seconds:null},interrupted=false;
for(let j=i+1;j<a.length;j++){const n=a[j],base={period:n.period,clock:clock(n),player:n.personId};if(n.period!==e.period||n.actionType==='period'){result=classify(reb,{...base,kind:'periodEnd'});break;}if(['timeout','substitution','violation'].includes(n.actionType))interrupted=true;
let next=null;
if(['2pt','3pt'].includes(n.actionType))next={...base,kind:n.teamId===e.teamId?'fg':'loss',zone:n.actionType==='3pt'?'long':/Restricted Area|In The Paint/.test(n.area??'')?'short':'mid',made:n.shotResult==='Made',points:n.shotResult==='Made'?(n.actionType==='3pt'?3:2):0,official:/putback|\btip\b/i.test((n.descriptor??'')+' '+(n.subType??''))};
else if(n.actionType==='turnover')next={...base,kind:'loss'};
else if(n.actionType==='rebound')next={...base,kind:n.teamId!==e.teamId?'loss':'unknown'};
else if(n.actionType==='foul'&&n.teamId!==e.teamId&&!/technical|flagrant|clearpath|awayfromplay|transitiontake/i.test((n.subType??'')+' '+(n.qualifiers??[]).join(' ')))next={...base,kind:'foul'};
else if(n.actionType==='freethrow'&&!/technical|flagrant|clearpath|awayfromplay|transitiontake/i.test((n.qualifiers??[]).join(' ')))next={...base,kind:n.teamId===e.teamId?'ft':'loss'};
if(next){result=classify(reb,next);break;}}
if(!Number.isFinite(reb.clock)||result.category==='invalidTime'){excluded.invalidTime++;continue;}rows.push({...result,interrupted,teamId:e.teamId,playerId:e.personId});}
games.push({id,rows});}catch(err){failures.push({id,error:err.message});}}
out[season]={games,missing,excluded,failures};console.log('REAL',season,games.length,games.reduce((s,g)=>s+g.rows.length,0),excluded);}
fs.writeFileSync(root+'/real.json',JSON.stringify(out)+'\n');
