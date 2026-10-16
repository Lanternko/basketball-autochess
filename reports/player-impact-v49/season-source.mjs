import {teamClockSeasonSource as previous} from '../player-impact-team-clock/season-source.mjs';
export function teamClockSeasonSource(){
 let s=previous();const a='simulateDefenseGame(...pair,{...options,seed:',b='simulateDefenseGame(...pair,{...options,rotationGameId:fixture.id,seed:';
 if(s.split(a).length!==2)throw Error('Rotation season anchor');s=s.replace(a,b);
 return s;
}
