"""Generate source preparation code from the independently checked v35 source reader."""
from pathlib import Path
R=Path('reports/player-impact-v36');R.mkdir(exist_ok=True)
s=Path('reports/player-impact-v35/prepare-data.mjs').read_text(encoding='utf-8')
def replace(a,b):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,b)
replace("import {loadInput} from './input.mjs';","import {loadInput} from '../player-impact-v30/input.mjs';")
replace("import {jointFlow} from './model.mjs';","import {priorFlow} from './model.mjs';")
s=s.replace("const root='reports/player-impact-v35'","const root='reports/player-impact-v36'")
s=s.replace('-conditional-data.json','-marked-data.json')
replace('const flow=jointFlow(ls);','const flow=priorFlow(ls);') if 'const flow=jointFlow(ls);' in s else replace('flow=jointFlow(ls);','flow=priorFlow(ls);')
replace('const supported=flow.self,unused=flow.self.map(()=>0);','const kernel=flow.kernel;')
replace('{attempts:0,selfMakes:0,assistedMakes:0}','{attempts:0,selfMakes:0,assistedMakes:0,passerMakes:[0,0,0,0,0]}')
replace('if(e.assistPersonId)count.assistedMakes++;else count.selfMakes++;',"if(e.assistPersonId){count.assistedMakes++;const j=[...s.teams[side].players].sort((a,b)=>a-b).indexOf(e.assistPersonId);assert.ok(j>=0&&e.assistPersonId!==e.personId);count.passerMakes[j]++;}else count.selfMakes++;")
replace('const pressure=pressureSignal(ds,b.options.stealPriorRate),attemptBase=[],attemptSlope=[],selfMakeBase=[],selfMakeSlope=[],assistedMake=[];', 'const pressure=pressureSignal(ds,b.options.stealPriorRate),features=[];')
replace('const own=predict(null),ownOut=survival(own);let a=supported[i]*ownOut.fga,sm=supported[i]*ownOut.makes,am=0;', 'const own=predict(null),ownOut=survival(own),d=kernel[i][i],assisted=Array(5).fill(0);let otherA=0,otherSelfM=0,otherMiss=0;')
replace('if(j!==i&&flow.matrix[j][i]>0)', 'if(j!==i&&kernel[j][i]>0)')
a='''      const lost=ls[j].opportunityMeasurement.passStolenPerMinute*pressure.relative,pass=flow.rows[j]+lost;
      const multiplier=pass*(1-Math.min(.95,lost/pass))/flow.rows[j];
      if(multiplier>1+1e-8)cappedInterceptions++;
      const incoming=flow.matrix[j][i]*multiplier;a+=incoming*out.fga;if(usedAssist)am+=incoming*out.makes;else sm+=incoming*out.makes;'''
b='''      // All source pass losses are far below the existing 0.95 cap. For any
      // selfScale this will also be checked before runtime use, not assumed.
      const incoming=kernel[j][i];otherA+=incoming*out.fga;
      otherMiss+=incoming*(out.fga-out.makes);
      if(usedAssist)assisted[j]=incoming*out.makes;else otherSelfM+=incoming*out.makes;'''
replace(a,b)
replace('attemptBase.push(a);attemptSlope.push(unused[i]*ownOut.fga);selfMakeBase.push(sm);selfMakeSlope.push(unused[i]*ownOut.makes);assistedMake.push(am);','features.push([d*ownOut.fga,otherA,d*ownOut.makes,otherSelfM,d*(ownOut.fga-ownOut.makes),otherMiss,assisted]);')
replace("assert.ok(attemptBase.every(v=>v>0));", "assert.ok(features.every(f=>f[0]>0&&f[1]>0&&f[2]>0&&f[4]>0));")
replace('rows.push([id,fold,s.teams[side].teamId,s.startIndex,s.endIndex,s.seconds,ids,n.map(x=>x.attempts),n.map(x=>x.selfMakes),n.map(x=>x.assistedMakes),attemptBase,attemptSlope,selfMakeBase,selfMakeSlope,assistedMake]);','rows.push([id,fold,s.teams[side].teamId,s.startIndex,s.endIndex,s.seconds,ids,n.map(x=>x.attempts),n.map(x=>x.selfMakes),n.map(x=>x.passerMakes),features]);')
replace("assert.ok(rows.some(r=>r[14].some(v=>v>0)),'No predicted assisted makes in a season');", "assert.ok(rows.some(r=>r[10].some(v=>v[6].some(x=>x>0))),'No assisted support');")
replace("columns:['gameId','gameFold','teamId','startIndex','endIndex','seconds','playerIds','attempts','selfMakes','assistedMakes','attemptBase','attemptSlope','selfMakeBase','selfMakeSlope','assistedMakeExpected']", "columns:['gameId','gameFold','teamId','startIndex','endIndex','seconds','playerIds','attempts','selfMakes','passerMakes','features']")
replace("design:'Joint creator/finisher flow v35: positive source self/pass prior balanced to normalized creator rows and terminal columns. attemptBase/selfMakeBase/assistedMakeExpected are fixed predictions; all slope columns zero. New source centering on identical source counts and mean-stint energy. Source full-season descriptors contain outcomes, not blind/causal. No fitted parameter or rank/name/wins coefficient.'", "featureColumns:['ownFga','otherFga','ownMade','otherSelfMade','ownMiss','otherMiss','assistedMadeByPasser'],design:'Positive source self/pass kernel projected to terminal columns only. One positive self/prior scale changes diagonal. Frozen v30 source contexts and probabilities, actual mean-stint fatigue, fresh FGA marks: miss, unassisted make, made by each other passer. Conditional on shooter/stint FGA, not blind or causal. Old three seasons only estimate scale; target reported separately. No fit to rank/wins/ONOFF.'")
(R/'prepare-marked.mjs').write_text(s,encoding='utf-8')
print('Prepared marked source reader')
