export function measuredPutbackChoice(player){
 const m=player.putbackChoiceMeasurement,p=m?.selectionProbabilityMAP;
 if(!Number.isFinite(p)||p<=0||p>=1)throw Error('Missing valid source putback selection tendency');
 return p;
}
