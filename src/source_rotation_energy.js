// Reference energy under observed game-clock rotations, using the same drain,
// bench recovery and period recovery equations as the simulation. This is a
// model reference, not a measurement of players' physiological fatigue.
const clamp=x=>Math.max(0,Math.min(1,x));
export function rotationEnergyStep(energy,seconds,playing,stamina){
 if(![energy,seconds,stamina].every(Number.isFinite)||energy<0||energy>1||seconds<0||stamina<0)throw Error('Invalid rotation energy input');
 const slope=playing?-1/(1800*(.6+Math.min(stamina,150)/175)):1/900,end=clamp(energy+slope*seconds);
 if(seconds===0)return {end,mean:energy};
 const bound=playing?0:1,time=Math.max(0,Math.min(seconds,(bound-energy)/slope));
 const mean=time<seconds?((energy+bound)*.5*time+bound*(seconds-time))/seconds:(energy+end)*.5;
 return {end,mean};
}
export function periodEnergyRecovery(energy,periods=1){return Math.min(1,energy+.12*periods);}
