import * as M from './probability_model.js';
import * as C from './constants.js';
import {inverse} from '../scripts/export_defense_sixth_cards.js';
import {read} from '../scripts/defense_io.js';
import {sixthInputs} from './defense_sixth_jobs.js';
import {runDefenseSeason} from './defense_seventh_season.js';
export function seventhInputs(job){
 const base=job.bundle?read(job.bundle):sixthInputs({cutoff:job.cutoff,options:job.options??{}});base.league=structuredClone(job.cardFile?read(job.cardFile):base.league);base.options={...base.options,...job.options};base.options.neutralContests=job.neutralContests??true;
 if(base.league.seventhSignals)base.options.defenseSignals=base.league.seventhSignals;
 if(base.league.sixthSignals)base.options.defenseSignals=base.league.sixthSignals;
 if(job.bundle&&job.cutoff>0){
  // Conditional active lists/starters remain supplied, but bench priority and
  // target minutes must not use a later game's observed seconds.
  const ps=new Map(base.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
  base.exposure={...base.exposure,games:base.exposure.games.map(g=>({...g,teams:g.teams.map(t=>({...t,players:t.players.map(p=>({...p,seconds:60*(ps.get(t.teamId).get(p.playerId)?.seasonMinutesPerGame??20)}))}))}))};
 }
 if(job.calibration){const c=job.calibration;base.options={...base.options,...c.options};for(const t of base.league.teams)for(const p of t.roster)for(const z of ['long','mid','short']){const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z],v=Math.max(.001,Math.min(.999,M.interpolate(p[z],curve))),shift=c.shotDelta??0;p[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-shift)),curve)));}}
 return base;
}
export function executeSeventhJob(job){const {league,exposure,options}=seventhInputs(job);const indices=job.indices??(job.calendarDate?league.schedule.flatMap((g,i)=>(job.phase==='train'?g.date<=job.calendarDate:g.date>job.calendarDate)?[i]:[]):null);return {...runDefenseSeason(league,exposure,{seed:job.seed,options,post41:!job.calendarDate&&job.cutoff>0,cutoff:job.cutoff,phase:job.phase??'post',audit:false,replay:false,indices}),preset:job.label,cutoff:job.cutoff,phase:job.phase??'post'};}
