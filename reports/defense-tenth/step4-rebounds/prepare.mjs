import fs from 'node:fs';
import {read,table,hash} from '../../../scripts/defense_io.js';
import {verify,root} from './run.mjs';
verify();const p=read(root+'/protocol.json');
const sum=a=>a.reduce((s,v)=>s+v,0),mean=a=>sum(a)/a.length,clip=(v,a,b)=>Math.max(a,Math.min(b,v));
for(const [f,h]of Object.entries(p.inputHashes))if(hash(f)!==h)throw Error('Changed input '+f);
const coverage=[];
for(const season of p.seasons){
 const base=season==='2025-26'?'data/season-source':`data/defense-seventh/${season}`,logs=table(base+'/player-games.json'),adv=table(`reports/defense-tenth/step4-t2/raw/${season}/0-advanced.json`),hustle=table(`reports/defense-tenth/step4-t2/raw/${season}/0-hustle.json`),b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`);
 const raw=new Map();for(const r of logs){const x=raw.get(r.PLAYER_ID)??{id:r.PLAYER_ID,name:r.PLAYER_NAME,minutes:0,dreb:0};x.minutes+=r.MIN??0;x.dreb+=r.DREB??0;raw.set(r.PLAYER_ID,x);}
 const aMap=new Map();for(const a of adv){if(aMap.has(a.PLAYER_ID))throw Error('Duplicate global advanced row '+a.PLAYER_ID);aMap.set(a.PLAYER_ID,a);}
 const valid=[...raw.values()].map(r=>({...r,share:aMap.get(r.id)?.DREB_PCT})).filter(r=>r.dreb>0&&r.share>0&&r.share<1&&r.minutes>0).map(r=>({...r,n:r.dreb/r.share})),fit=valid.filter(r=>r.minutes>=500);
 const mu=sum(fit.map(r=>r.dreb))/sum(fit.map(r=>r.n)),avg=mean(fit.map(r=>r.share)),variance=mean(fit.map(r=>(r.share-avg)**2)),noise=mean(fit.map(r=>mu*(1-mu)/r.n)),kappa=clip(mu*(1-mu)/Math.max(variance-noise,1e-6)-1,1,10000),opportunitiesPerMinute=sum(valid.map(r=>r.n))/sum(valid.map(r=>r.minutes));
 const players={},ids=new Set(b.league.teams.flatMap(t=>t.roster.map(p=>p.playerId))),missing=[];
 for(const id of ids){const r=raw.get(id),a=aMap.get(id),rate=a?.DREB_PCT;let n=0,share=mu,flag=null;if(r&&Number.isFinite(rate)&&rate>=0&&rate<1){n=r.dreb>0&&rate>0?r.dreb/rate:r.minutes*opportunitiesPerMinute;share=(r.dreb+kappa*mu)/(n+kappa);}else{flag='Missing official DREB_PCT; pooled individual prior';missing.push(id);}players[id]={id,name:r?.name??b.league.teams.flatMap(t=>t.roster).find(p=>p.playerId===id)?.name,share,rawShare:rate??null,dreb:r?.dreb??null,minutes:r?.minutes??0,opportunities:n,flag};}
 const hs=new Map(hustle.map(r=>[r.PLAYER_ID,r])),allMinutes=sum([...raw.values()].map(r=>r.minutes)),boxSummary={players:hustle.length,minuteCoverage:sum([...raw.values()].filter(r=>hs.has(r.id)).map(r=>r.minutes))/allMinutes,totalBoxouts:sum(hustle.map(r=>r.BOX_OUTS??0)),defensiveBoxouts:sum(hustle.map(r=>r.DEF_BOXOUTS??0)),selfRebounds:sum(hustle.map(r=>r.BOX_OUT_PLAYER_REBS??0)),teamRebounds:sum(hustle.map(r=>r.BOX_OUT_PLAYER_TEAM_REBS??0)),teammateRebounds:sum(hustle.map(r=>(r.BOX_OUT_PLAYER_TEAM_REBS??0)-(r.BOX_OUT_PLAYER_REBS??0))),note:'Offense and defense not separated for rebound recipients; teammate recovery already counted elsewhere, not an additional rebound.'};
 const c={season,mu,kappa,variance,noise,fitPlayers:fit.length,opportunitiesPerMinute,players,missing,boxSummary};fs.mkdirSync(root+'/'+season,{recursive:true});fs.writeFileSync(root+'/'+season+'/cards.json',JSON.stringify(c,null,2)+'\n');coverage.push({season,players:ids.size,missing,minuteCoverage:sum([...raw.values()].filter(r=>ids.has(r.id)&&!missing.includes(r.id)).map(r=>r.minutes))/allMinutes,mu,kappa,boxSummary});
}
fs.writeFileSync(root+'/coverage.json',JSON.stringify(coverage,null,2)+'\n');console.log(JSON.stringify(coverage));
