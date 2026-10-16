import {read,table} from '../../../scripts/defense_io.js';
import * as C from '../../../src/constants.js';
import * as M from '../../../src/probability_model.js';
import {inverse as calibratedInverse} from '../../../scripts/export_defense_sixth_cards.js';
export const attrs=['long','mid','short','ft','drive','tovSkill','pass','rebound','onBall','help'];
export const rates=['fgaPerMinute','tovPerMinute','stlPerMinute','threeAttemptShare','freeThrowsPerAttempt'];
export const features=[...attrs,...rates];
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length,safe=(a,b)=>b>0?a/b:0,sum=(a,k)=>a.reduce((s,x)=>s+(x[k]??0),0);
const attr=q=>Math.max(40,Math.min(99,q<50?40+(q-1)*30/49:70+(q-50)*29/49));
const rank=(v,a)=>attr(100*(a.filter(x=>x<v).length+.5*a.filter(x=>x===v).length)/a.length);
function inverse(v,c){for(let i=1;i<c.length;i++){const[a,b]=c[i-1],[x,y]=c[i];if(v>=Math.min(b,y)&&v<=Math.max(b,y))return Math.max(40,Math.min(99,a+(v-b)/(y-b)*(x-a)));}return Math.abs(v-c[0][1])<Math.abs(v-c.at(-1)[1])?40:99;}
export const paths=s=>s==='2025-26'?{logs:'data/season-source/player-games.json',bio:'data/benchmark-source/bio.json',league:'data/season-league.json',manifest:'data/defense-a-source/manifest.json'}:{logs:`data/defense-seventh/${s}/player-games.json`,bio:`data/defense-seventh/${s}/bio.json`,league:`data/defense-seventh/${s}/league.json`,manifest:`data/defense-seventh/${s}/manifest.json`};
export function buildCards(season){
 const f=paths(season),stats=new Map();for(const r of table(f.logs))if(r.MIN>0){const q=stats.get(r.PLAYER_ID)??{playerId:r.PLAYER_ID,name:r.PLAYER_NAME,GP:0};q.GP++;for(const z of ['MIN','PTS','FGM','FGA','FG3M','FG3A','FTM','FTA','OREB','DREB','REB','AST','TOV','STL','BLK','PF'])q[z]=(q[z]??0)+(r[z]??0);stats.set(r.PLAYER_ID,q);}
 const rows=[...stats.values()],pool=rows.filter(q=>q.GP>=15&&q.MIN/q.GP>=20),bio=new Map(table(f.bio).map(q=>[q.PLAYER_ID,q])),meta=new Map(read(f.league).teams.flatMap(t=>t.roster).map(q=>[q.playerId,q])),tracked=new Map(read(`reports/defense-seventh/${season}/calendar-55/v3-league.json`).teams.flatMap(t=>t.roster).map(q=>[q.playerId,{onBall:q.onBall,help:q.help}])),shots=new Map();
 for(const s of read(f.manifest).sources)for(const e of read(s.file).data.game.actions)if(e.isFieldGoal===1&&['2pt','3pt'].includes(e.actionType)){const q=shots.get(e.personId)??{},z=e.actionType==='3pt'?'long':e.area==='Mid-Range'?'mid':'short';q[z+'A']=(q[z+'A']??0)+1;q[z+'M']=(q[z+'M']??0)+(e.shotResult==='Made');shots.set(e.personId,q);}
 const priors={long:sum(rows,'FG3M')/sum(rows,'FG3A'),ft:sum(rows,'FTM')/sum(rows,'FTA'),mid:sum([...shots.values()],'midM')/sum([...shots.values()],'midA'),short:sum([...shots.values()],'shortM')/sum([...shots.values()],'shortA')};
 const ff={drive:q=>safe(q.FTA,q.FGA),tovSkill:q=>-safe(q.TOV,q.FGA+.44*q.FTA+q.AST+q.TOV),pass:q=>bio.get(q.playerId)?.AST_PCT??0,rebound:q=>(bio.get(q.playerId)?.OREB_PCT??0)+(bio.get(q.playerId)?.DREB_PCT??0),stamina:q=>q.MIN/q.GP,physique:q=>{const m=meta.get(q.playerId);return m.heightInches+m.bodyWeight/10;}};
 const cards=new Map(rows.map(q=>{const m=meta.get(q.playerId),s=shots.get(q.playerId)??{},shoot=(z,a,n,c)=>inverse((a+100*priors[z])/(n+100),c);return[q.playerId,{playerId:q.playerId,name:q.name,pos:m.pos,courtPosition:m.pos,heightInches:m.heightInches,bodyWeight:m.bodyWeight,long:shoot('long',q.FG3M,q.FG3A,C.CURVE_3PT),mid:shoot('mid',s.midM??0,s.midA??0,C.CURVE_MID),short:shoot('short',s.shortM??0,s.shortA??0,C.CURVE_SHORT),ft:shoot('ft',q.FTM,q.FTA,C.CURVE_FT),...Object.fromEntries(Object.entries(ff).map(([k,f])=>[k,rank(f(q),pool.map(f))])),onBall:tracked.get(q.playerId)?.onBall??70,help:tracked.get(q.playerId)?.help??70,offBall:70,screen:70,handle:70,breakDbl:70,shotProfile:{threeRate:safe(q.FG3A,q.FGA),freeThrowsPerAttempt:safe(q.FTA,q.FGA),sourceSeason:season},seasonMinutesPerGame:q.MIN/q.GP,defenseMeasurement:{steals:q.STL,minutes:q.MIN},offenseMeasurement:{attempts:q.FGA,freeThrows:q.FTA,turnovers:q.TOV,minutes:q.MIN},observed:Object.fromEntries(Object.entries(q).filter(([k])=>!['playerId','name'].includes(k))),abilitySource:season}];}));
 const values=q=>({...Object.fromEntries(attrs.map(k=>[k,q[k]])),fgaPerMinute:q.offenseMeasurement.attempts/q.offenseMeasurement.minutes,tovPerMinute:q.offenseMeasurement.turnovers/q.offenseMeasurement.minutes,stlPerMinute:q.defenseMeasurement.steals/q.defenseMeasurement.minutes,threeAttemptShare:q.shotProfile.threeRate,freeThrowsPerAttempt:q.shotProfile.freeThrowsPerAttempt});
 const minutes=rows.reduce((s,q)=>s+q.MIN,0),means=Object.fromEntries(features.map(k=>[k,[...cards.values()].reduce((s,q)=>s+values(q)[k]*q.observed.MIN,0)/minutes]));
 return{season,cards,stats,bio,means,values,priors};
}
export const ageGroup=a=>a<=22?'<=22':a<=26?'23-26':a<=30?'27-30':a<=34?'31-34':'35+';
export function shrunk(data,q){const v=data.values(q),w=Math.min(1,q.observed.MIN/500);return Object.fromEntries(features.map(k=>[k,data.means[k]+w*(v[k]-data.means[k])]));}
export function aged(data,old,curve){const q=structuredClone(data.cards.get(old.playerId)),age=data.bio.get(q.playerId)?.AGE,values=shrunk(data,q),delta=Number.isFinite(age)?curve.groups[ageGroup(age)].delta:Object.fromEntries(features.map(k=>[k,0]));
 for(const k of attrs)q[k]=Math.max(0,Math.min(120,values[k]+delta[k]));
 const r=Object.fromEntries(rates.map(k=>[k,Math.max(0,values[k]+delta[k])])),n=q.observed.MIN;
 q.shotProfile={...q.shotProfile,threeRate:Math.min(1,r.threeAttemptShare),freeThrowsPerAttempt:r.freeThrowsPerAttempt};q.offenseMeasurement={attempts:r.fgaPerMinute*n,turnovers:r.tovPerMinute*n,freeThrows:r.fgaPerMinute*r.freeThrowsPerAttempt*n,minutes:n};q.defenseMeasurement={steals:r.stlPerMinute*n,minutes:n};return q;
}
export function calibrate(raw,origin){const q=structuredClone(raw),c=read(`reports/defense-seventh/${origin}/calendar-55/calibration-v3.json`).selected;for(const z of ['long','mid','short']){const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z],v=Math.max(.001,Math.min(.999,M.interpolate(q[z],curve)));q[z]=Math.max(0,Math.min(120,calibratedInverse(1/(1+Math.exp(-Math.log(v/(1-v))-(c.shotDelta??0))),curve)));}return q;}
