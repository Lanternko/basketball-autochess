from pathlib import Path
root=Path('reports/player-impact-v2')
s=Path('reports/player-impact-v1/engine.mjs').read_text(encoding='utf-8')
s=s.replace("['control','creation-flow','creation-flow-balanced']","['opportunity-flow']")
start=s.index(" if(version!=='control'){");end=s.index(' // Keep the already verified',start)
block=r''' {
  // Move this closure ahead of handler selection. It does not capture hi.
  patches.push(`{const start=g.indexOf('    const probability = (i,a=null,forced=false) => {'),end=g.indexOf('    const best = (i,a,forced=false) => {',start);if(start<0||end<0)throw Error('Probability closure drift');const p=g.slice(start,end);g=g.slice(0,start)+g.slice(end);const anchor='    let hi=putback===null?';if(g.split(anchor).length!==2)throw Error('Selection anchor drift');g=g.replace(anchor,p+'    const creationPlan=putback===null?opportunityPlan(ls[off],probability,pressureSignal(ls[1-off],opt.stealPriorRate).relative):null;\\n'+anchor);}`);
  replace("volumeWeights(ls[off]):M.handlingWeights(ls[off])","creationPlan.weights:M.handlingWeights(ls[off])");
  replace('M.shootRate(p.ev,passesLeft)','(passesLeft===C.MAX_PASSES?creationPlan.rows[hi].shoot:1)');
  replace('M.passOpenRate(ls[off][hi],M.teammateContext(ls[off],hi),pressureDefender)','1');
  replace('M.interceptRate(ls[off][hi],pressureDefender,M.teammateContext(ls[off],hi))*(opt.turnoverCategories?opt.passTurnoverScale:1)','creationPlan.rows[hi].intercept');
  replace("volumeWeights(ls[off],'shot').map((w,i)=>i===hi?0:w)",'creationPlan.rows[hi].receivers');
  patches.push(`g="import {opportunityPlan} from '${url('reports/player-impact-v2/model.mjs')}';\\n"+g;`);
 }
'''
s=s[:start]+block+s[end:]
(root/'engine.mjs').write_text(s,encoding='utf-8')
worker=Path('reports/player-impact-v1/worker.mjs').read_text(encoding='utf-8').replace("from './on-court.mjs'","from '../player-impact-v1/on-court.mjs'")
(root/'worker.mjs').write_text(worker,encoding='utf-8')
