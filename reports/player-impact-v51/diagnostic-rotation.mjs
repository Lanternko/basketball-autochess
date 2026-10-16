import {measuredRotate,observeRotationInterval as observe} from './deadline-rotation.mjs';
export {measuredRotate};
export function observeRotationInterval(sides,seconds,opt){observe(sides,seconds,opt);opt.rotationDiagnosticObserver?.({gameId:opt.rotationGameId,teams:sides.map(s=>({teamId:s.rotationTeamId,players:s.roster.map((p,i)=>({playerId:p.playerId,target:p.targetMinutes??0,pf:s.players[i].pf,regulationSeconds:s.players[i].regulationSeconds}))}))});}
