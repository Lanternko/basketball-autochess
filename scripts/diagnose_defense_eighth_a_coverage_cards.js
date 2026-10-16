import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {createRater} from './export_defense_sixth_cards.js';
const root='reports/defense-eighth/a/coverage',rules=read(root+'/rules.json');
for(const k of [25,41,55])for(const dir of [`reports/defense-seventh/2025-26/calendar-${k}`,...rules.maskSeeds.map(s=>`${root}/mask-${s}/calendar-${k}`)]){
 const bundle=read(dir+'/bundle.json'),league=read(dir+`/pre${k}-v4-league.json`),options={...bundle.options,neutralContests:true,defenseSignals:league.seventhSignals},r=createRater(league,options),ps=new Map();
 for(const t of league.teams)for(const p of t.roster)if(!ps.has(p.playerId))ps.set(p.playerId,{id:p.playerId,...r.value(p)});
 // Diagnostic derived artifacts go under eighth only, never frozen directories.
 const out=dir.startsWith(root)?dir:root+`/full/calendar-${k}`;fs.mkdirSync(out,{recursive:true});fs.writeFileSync(out+'/deployed-card-values.json',JSON.stringify({players:[...ps.values()],cardHash:hash(dir+`/pre${k}-v4-league.json`),definition:'Neutral deployment context, analytic isolated-player EV; no league calibration, clock/rebound recursion or game simulation. Heldout exposure is evaluation-only.'})+'\n');
}
