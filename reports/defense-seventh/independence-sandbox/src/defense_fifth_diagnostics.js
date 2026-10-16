export function compressDiagnosticGames(normal){return normal.map(g=>{
 const cells={},N=[0,0],points=[0,0];
 for(const p of g.possessions){if(p.period>4)continue;N[p.side]++;points[p.side]+=p.points;
  const remaining=(4-p.period)*720+p.start,time=[2160,1440,720,360,120,0].findIndex(x=>remaining>=x),lead=p.lead,bin=lead<=-20?'<=-20':lead<=-10?'-19..-10':lead<=-6?'-9..-6':lead<=5?'-5..5':lead<=9?'6..9':lead<=19?'10..19':'>=20';
  const key=p.side+':'+time+':'+bin,c=cells[key]??={side:p.side,time,lead:bin,n:0,points:0,duration:0};c.n++;c.points+=p.points;c.duration+=p.duration;
 }
 return {id:g.id,ids:g.ids,N,points,S:g.regulationScore??g.score,q3:g.q3,box:g.box,cells:Object.values(cells)};
});}
