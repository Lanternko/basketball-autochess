import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
import {buildCards,features,ageGroup,shrunk,paths} from './cards.mjs';
const d='reports/defense-tenth/step3-a2',p=read(d+'/protocol.json');if(fs.existsSync(d+'/curve-lock.json'))throw Error('Coefficients locked; do not overwrite');
const seasons=['2022-23','2023-24','2024-25'],data=new Map(seasons.map(s=>{console.log('READ PERSONAL',s);return[s,buildCards(s)];})),pairs=[['2022-23','2023-24'],['2023-24','2024-25']];
function fit(ps){const groups=Object.fromEntries(p.ages.groups.map(k=>[k,{n:0,observed:0,disappeared:0,lowOrMissing:0,sum:Object.fromEntries(features.map(k=>[k,0]))}]));
 for(const[a,b]of ps){const x=data.get(a),y=data.get(b);for(const q of x.cards.values()){const age=x.bio.get(q.playerId)?.AGE;if(!Number.isFinite(age))throw Error('Missing training age');const z=groups[ageGroup(age)],n=y.cards.get(q.playerId);z.n++;if(!n){z.disappeared++;z.lowOrMissing++;continue;}z.observed++;if(n.observed.GP<15||n.observed.MIN<300)z.lowOrMissing++;const before=shrunk(x,q),after=shrunk(y,n);for(const k of features)z.sum[k]+=after[k]-before[k];}}
 for(const z of Object.values(groups)){z.delta=Object.fromEntries(features.map(k=>[k,z.sum[k]/(z.n+p.curves.agePseudoPlayers)]));z.observedOnlyDelta=Object.fromEntries(features.map(k=>[k,z.sum[k]/(z.observed+p.curves.agePseudoPlayers)]));z.disappearanceShare=z.disappeared/z.n;}
 return{pairs:ps,groups};}
const curves={'2025-26':fit(pairs),'2023-24':fit([pairs[1]]),'2024-25':fit([pairs[0]])};
fs.writeFileSync(d+'/curves.json',JSON.stringify({createdAt:new Date().toISOString(),protocolHash:hash(d+'/protocol.json'),curves},null,2)+'\n');
const files=[...seasons.flatMap(s=>Object.values(paths(s))),...seasons.map(s=>`reports/defense-seventh/${s}/calendar-55/v3-league.json`),'data/defense-a-source/manifest.json',...['cards.mjs','fit.mjs'].map(x=>d+'/'+x)];
const lock={lockedAt:new Date().toISOString(),protocolHash:hash(d+'/protocol.json'),curveHash:hash(d+'/curves.json'),coefficientCountMain:75,coefficientCountEachReference:75,files:Object.fromEntries(files.map(f=>[f,hash(f)]))};fs.writeFileSync(d+'/curve-lock.json',JSON.stringify(lock,null,2)+'\n');fs.writeFileSync(d+'/curve-lock.sha256',hash(d+'/curve-lock.json')+'\n');console.log('LOCK',JSON.stringify({sha256:hash(d+'/curve-lock.json'),at:lock.lockedAt}));
