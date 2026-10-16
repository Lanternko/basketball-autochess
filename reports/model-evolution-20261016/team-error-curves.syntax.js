
(()=>{
const root=document.getElementById('model-team-curves');
const data={"kind":"team","versions":[14,17,19,20,21,22,23,24,25,26,28,30,31,34,35,36,37,39,41],"values":{"control":{"winsMAE":6.022222222222223,"netRMSE":3.362420352030198,"pts":2.2013550135501343,"ast":4.1807588075880755,"oreb":0.3959349593495933,"dreb":1.2318428184281836,"reb":1.141327913279132,"stl":0.3173441734417345,"blk":0.5787262872628727,"tov":0.828048780487805,"fgPct":0.7146625902891409,"threePct":0.7786393068542314,"ftPct":0.9284779470491952},"14":{"winsMAE":5.733333333333333,"netRMSE":2.912484230117747,"pts":2.2455284552845525,"ast":1.4584010840108403,"oreb":0.4157181571815718,"dreb":1.4384823848238482,"reb":1.6883468834688344,"stl":0.1699186991869919,"blk":0.49715447154471537,"tov":0.7447154471544715,"fgPct":0.6608218732268841,"threePct":0.6205782193129733,"ftPct":0.8996361922177291},"17":{"winsMAE":5.9111111111111105,"netRMSE":3.0084241414902313,"pts":2.448509485094852,"ast":1.512737127371274,"oreb":0.44092140921409223,"dreb":1.4850948509485098,"reb":1.7531165311653116,"stl":0.18455284552845527,"blk":0.5031165311653116,"tov":0.7238482384823848,"fgPct":0.7501362961661168,"threePct":0.6396203907059823,"ftPct":0.8722803306208019},"19":{"winsMAE":6.711111111111111,"netRMSE":3.1701093823297253,"pts":2.4433604336043375,"ast":0.5208672086720866,"oreb":0.3365853658536586,"dreb":1.30230352303523,"reb":1.4971544715447151,"stl":0.1746612466124662,"blk":0.5107046070460705,"tov":0.7093495934959348,"fgPct":0.8101642569491039,"threePct":0.7260169584557071,"ftPct":0.935639937250028},"20":{"winsMAE":7.644444444444445,"netRMSE":3.4962344675381365,"pts":2.3955284552845524,"ast":0.5360433604336042,"oreb":0.3398373983739837,"dreb":1.2018970189701896,"reb":1.3842818428184283,"stl":0.1674796747967479,"blk":0.46720867208672084,"tov":0.7071815718157181,"fgPct":0.8536918172601724,"threePct":0.6534907441995611,"ftPct":0.8884290322225226},"21":{"winsMAE":8.022222222222222,"netRMSE":3.688521209160071,"pts":2.361653116531165,"ast":0.4957994579945794,"oreb":0.3040650406504064,"dreb":1.1779132791327913,"reb":1.3242547425474251,"stl":0.197560975609756,"blk":0.48360433604336045,"tov":0.5523035230352302,"fgPct":0.7393630472421552,"threePct":0.5081417397788693,"ftPct":0.9515435646011572},"22":{"winsMAE":7.844444444444444,"netRMSE":3.6164899409851765,"pts":2.1624661246612473,"ast":0.49376693766937657,"oreb":0.2814363143631436,"dreb":1.1468834688346883,"reb":1.2852303523035224,"stl":0.21273712737127365,"blk":0.4723577235772358,"tov":0.5567750677506775,"fgPct":0.591990586028148,"threePct":0.554184506451412,"ftPct":0.8810285344519131},"23":{"winsMAE":7.955555555555557,"netRMSE":3.623919788409284,"pts":2.3550135501355016,"ast":0.5456639566395663,"oreb":0.3226287262872628,"dreb":1.1311653116531162,"reb":1.3464769647696468,"stl":0.18780487804878054,"blk":0.4924119241192412,"tov":0.6294037940379404,"fgPct":0.5780443059549987,"threePct":0.5142984823382383,"ftPct":0.8905399878664574},"24":{"winsMAE":7.955555555555557,"netRMSE":3.623919788409284,"pts":2.3550135501355016,"ast":0.5456639566395663,"oreb":0.3226287262872628,"dreb":1.1311653116531162,"reb":1.3464769647696468,"stl":0.18780487804878054,"blk":0.4924119241192412,"tov":0.6294037940379404,"fgPct":0.5780443059549987,"threePct":0.5142984823382383,"ftPct":0.8905399878664574},"25":{"winsMAE":6.622222222222222,"netRMSE":3.3768181192221345,"pts":2.3955284552845537,"ast":0.5033875338753389,"oreb":0.32168021680216796,"dreb":1.1865853658536587,"reb":1.3708672086720868,"stl":0.23875338753387532,"blk":0.46233062330623304,"tov":0.6521680216802167,"fgPct":0.7227258256815755,"threePct":0.7465759058118925,"ftPct":0.8884779196551074},"26":{"winsMAE":7.311111111111112,"netRMSE":3.5051721413314594,"pts":2.589024390243901,"ast":0.5440379403794035,"oreb":0.33035230352303524,"dreb":1.1891598915989159,"reb":1.3775067750677505,"stl":0.20880758807588082,"blk":0.48672086720867214,"tov":0.6383468834688348,"fgPct":0.7864716141934023,"threePct":0.722989140790942,"ftPct":0.7922773677969752},"28":{"winsMAE":7.222222222222222,"netRMSE":3.458742729849841,"pts":2.5798102981029802,"ast":0.533739837398374,"oreb":0.33997289972899725,"dreb":1.1673441734417347,"reb":1.3945799457994583,"stl":0.21097560975609753,"blk":0.49159891598915983,"tov":0.6466124661246611,"fgPct":0.7827514230960441,"threePct":0.735005006622765,"ftPct":0.8425966635122879},"30":{"winsMAE":6.911111111111111,"netRMSE":3.3913150712692772,"pts":2.5472899728997302,"ast":0.5283197831978323,"oreb":0.3531165311653116,"dreb":1.1861788617886175,"reb":1.4051490514905143,"stl":0.21639566395663953,"blk":0.5112466124661246,"tov":0.643631436314363,"fgPct":0.7627108732399245,"threePct":0.7157415551587154,"ftPct":0.7696455401925403},"31":{"winsMAE":7.177777777777778,"netRMSE":3.3838833446802994,"pts":2.5998644986449855,"ast":1.3621951219512196,"oreb":0.33265582655826553,"dreb":1.1210027100271003,"reb":1.3539295392953932,"stl":0.25176151761517623,"blk":0.4726287262872628,"tov":0.7594850948509484,"fgPct":0.7424386450969308,"threePct":0.7582628242402542,"ftPct":0.8169779205904555},"34":{"winsMAE":6.4,"netRMSE":3.060529484471245,"pts":2.4724932249322484,"ast":1.6636856368563682,"oreb":0.2897018970189702,"dreb":1.1353658536585367,"reb":1.240514905149052,"stl":0.19498644986449867,"blk":0.47154471544715443,"tov":0.5666666666666667,"fgPct":0.6575583789226409,"threePct":0.8455093796691654,"ftPct":0.7893655142391647},"35":{"winsMAE":6.888888888888888,"netRMSE":3.323937945466108,"pts":2.5318428184281845,"ast":0.587127371273713,"oreb":0.31693766937669376,"dreb":1.1074525745257453,"reb":1.3195121951219515,"stl":0.21856368563685638,"blk":0.4952574525745258,"tov":0.5888888888888888,"fgPct":0.7042287833174665,"threePct":0.676745004694569,"ftPct":0.7673043840917748},"36":{"winsMAE":6.777777777777777,"netRMSE":3.37242511424801,"pts":2.3890243902439012,"ast":0.6158536585365855,"oreb":0.31680216802168015,"dreb":1.0505420054200543,"reb":1.2781842818428184,"stl":0.23021680216802173,"blk":0.48915989159891604,"tov":0.5886178861788618,"fgPct":0.5846563281512029,"threePct":0.5755170599659738,"ftPct":0.8708398075611974},"37":{"winsMAE":6.866666666666668,"netRMSE":3.1655718560682575,"pts":2.325880758807587,"ast":0.538482384823848,"oreb":0.2753387533875337,"dreb":1.2668021680216799,"reb":1.3968834688346874,"stl":0.26300813008130075,"blk":0.4976964769647696,"tov":0.6262872628726287,"fgPct":0.5347982515609365,"threePct":0.5231065022632356,"ftPct":0.8152351071788614},"39":{"winsMAE":6.911111111111111,"netRMSE":3.3913150712692772,"pts":2.5472899728997302,"ast":0.5283197831978323,"oreb":0.3531165311653116,"dreb":1.1861788617886175,"reb":1.4051490514905143,"stl":0.21639566395663953,"blk":0.2481029810298103,"tov":0.643631436314363,"fgPct":0.7627108732399245,"threePct":0.7157415551587154,"ftPct":0.7696455401925403},"41":{"winsMAE":6.666666666666667,"netRMSE":2.875962298516054,"pts":2.415718157181572,"ast":0.5794037940379405,"oreb":0.35907859078590765,"dreb":1.1136856368563683,"reb":1.3532520325203252,"stl":0.18495934959349603,"blk":0.22615176151761515,"tov":0.5487804878048779,"fgPct":0.739405782873279,"threePct":0.7056596082636979,"ftPct":1.0311465224111194}},"groups":[{"title":"整季勝場","unit":"勝","metrics":[{"key":"winsMAE","label":"勝場誤差","color":1}],"error":"MAE"},{"title":"每場淨得分","unit":"分／場","metrics":[{"key":"netRMSE","label":"淨分誤差","color":1}],"error":"RMSE"},{"title":"得分","unit":"分／場","metrics":[{"key":"pts","label":"得分","color":1}],"error":"MAE"},{"title":"助攻與總籃板","unit":"次／場","metrics":[{"key":"ast","label":"助攻","color":2},{"key":"reb","label":"籃板","color":3}],"error":"MAE"},{"title":"進攻與防守籃板","unit":"次／場","metrics":[{"key":"oreb","label":"進攻籃板","color":4},{"key":"dreb","label":"防守籃板","color":5}],"error":"MAE"},{"title":"失誤、抄截與阻攻","unit":"次／場","metrics":[{"key":"tov","label":"失誤","color":1},{"key":"stl","label":"抄截","color":2},{"key":"blk","label":"阻攻","color":3}],"error":"MAE"},{"title":"命中率","unit":"百分點","metrics":[{"key":"fgPct","label":"投籃","color":1},{"key":"threePct","label":"三分","color":2},{"key":"ftPct","label":"罰球","color":3}],"error":"MAE"}]};
const ns='http://www.w3.org/2000/svg';
const hidden=new Set();let references=true;
const saved=window.openai?.widgetState?.privateContent;
if(saved?.chart===root.id){(saved.hidden||[]).forEach(k=>hidden.add(k));references=saved.references!==false;}
const tooltip=root.querySelector('.curve-tooltip'),grid=root.querySelector('.plot-grid'),status=root.querySelector('.sr-only');
const refButton=root.querySelector('.reference-key');
const format=v=>v>=10?v.toFixed(2):v.toFixed(3);
const color=k=>`var(--viz-series-${k})`;
const persist=()=>window.openai?.setWidgetState?.({modelContent:{chart:data.kind,hiddenMetrics:[...hidden],showOfficialBaseline:references},privateContent:{chart:root.id,hidden:[...hidden],references}})?.catch(()=>{});
const panels=[];
const svgElement=(tag,attrs={})=>{const e=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);return e;};
function readState(state){const p=state?.privateContent;if(p?.chart!==root.id)return;hidden.clear();(p.hidden||[]).forEach(k=>hidden.add(k));references=p.references!==false;update(false);}
window.addEventListener('openai:set_globals',e=>readState(e.detail?.globals?.widgetState));
for(const group of data.groups){
 const section=document.createElement('section');section.className='plot';
 const title=document.createElement('div');title.className='plot-title';title.textContent=group.title;
 const keys=document.createElement('div');keys.className='plot-keys text-small';
 const holder=document.createElement('div');holder.className='plot-holder';
 const svg=svgElement('svg',{class:'curve-chart',role:'img','aria-label':`${group.title}，橫軸模型版本，縱軸${group.unit}誤差；越低越準。`});holder.append(svg);
 for(const metric of group.metrics){
  const b=document.createElement('button');b.type='button';b.className='series-key cursor-interaction';b.dataset.metric=metric.key;
  const sw=document.createElement('i');sw.style.background=color(metric.color);sw.setAttribute('aria-hidden','true');
  const label=document.createElement('span');label.textContent=`${metric.label} ${format(data.values['41'][metric.key])}`;
  b.append(sw,label);b.setAttribute('aria-label',`${metric.label}，v41 ${format(data.values['41'][metric.key])} ${group.unit}；切換顯示`);
  b.addEventListener('click',()=>{hidden.has(metric.key)?hidden.delete(metric.key):hidden.add(metric.key);update(true);persist();});keys.append(b);
 }
 section.append(title,keys,holder);grid.append(section);panels.push({group,holder,svg,drawn:false});
}
function draw(panel,animate){
 const {svg,holder,group}=panel,width=Math.max(280,holder.getBoundingClientRect().width),height=256;
 const margin={left:64,right:15,top:17,bottom:49},frame={x:margin.left,y:margin.top,w:width-margin.left-margin.right,h:height-margin.top-margin.bottom};
 const active=group.metrics.filter(m=>!hidden.has(m.key));
 const all=[];for(const m of active){for(const v of data.versions)all.push(data.values[v][m.key]);if(references)all.push(data.values.control[m.key]);}
 let lo,hi;[lo,hi]=d3.extent(all.length?all:[0,1]);const pad=Math.max((hi-lo)*.12,hi*.025,.0001);
 const x=d3.scaleLinear().domain(d3.extent(data.versions)).range([frame.x+4,frame.x+frame.w-4]);
 const y=d3.scaleLinear().domain([Math.max(0,lo-pad),hi+pad]).nice(4).range([frame.y+frame.h-4,frame.y+4]);
 const old=panel.drawn,prev=panel.coords;panel.coords={x,y};
 svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.setAttribute('height',height);svg.replaceChildren();
 const desc=svgElement('desc');desc.textContent=group.metrics.map(m=>`${m.label}：v14 ${format(data.values['14'][m.key])}，v41 ${format(data.values['41'][m.key])}，正式模型 ${format(data.values.control[m.key])} ${group.unit}`).join('；');svg.append(desc);
 const frameRect=svgElement('rect',{'data-chart-frame':'',x:frame.x,y:frame.y,width:frame.w,height:frame.h,fill:'none',stroke:'var(--border)','stroke-width':1});svg.append(frameRect);
 const ticks=width<400?[14,24,30,41]:[14,20,24,30,41];
 const gx=d3.select(svg).append('g').attr('transform',`translate(0,${frame.y+frame.h})`).call(d3.axisBottom(x).tickValues(ticks).tickFormat(v=>`v${v}`).tickSizeOuter(0));
 gx.select('.domain').remove();gx.selectAll('text').attr('dy','1.15em');
 const gy=d3.select(svg).append('g').attr('transform',`translate(${frame.x},0)`).call(d3.axisLeft(y).ticks(4).tickFormat(d3.format('.2~f')).tickSizeOuter(0));gy.select('.domain').remove();
 for(const t of y.ticks(4)){svg.append(svgElement('line',{x1:frame.x,x2:frame.x+frame.w,y1:y(t),y2:y(t),stroke:'var(--border)','stroke-width':.5,'pointer-events':'none'}));}
 const xt=svgElement('text',{class:'axis-title','data-axis':'x',x:frame.x+frame.w/2,y:height-3,'text-anchor':'middle'});xt.textContent='模型版本';svg.append(xt);
 const yt=svgElement('text',{class:'axis-title','data-axis':'y',transform:`translate(15,${frame.y+frame.h/2}) rotate(-90)`,'text-anchor':'middle'});yt.textContent=`${group.error||'MAE'}（${group.unit}）`;svg.append(yt);
 const line=d3.line().x(d=>x(d.x)).y(d=>y(d.y));
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const change=animate&&old&&!reduced;
 for(const m of active){
  const vals=data.versions.map(v=>({x:v,y:data.values[v][m.key]}));
  if(references){const path=svgElement('line',{x1:x(data.versions[0]),x2:x(data.versions.at(-1)),y1:y(data.values.control[m.key]),y2:y(data.values.control[m.key]),stroke:color(m.color),'stroke-width':1.2,'stroke-dasharray':'4 4',opacity:.65});svg.append(path);}
  const p=svgElement('path',{d:line(vals),fill:'none',stroke:color(m.color),'stroke-width':2});svg.append(p);
  if(change){const prior=d3.line().x(d=>prev.x(d.x)).y(d=>prev.y(d.y));d3.select(p).attr('d',prior(vals)).transition().duration(240).attr('d',line(vals));}
  for(const d of vals){const c=svgElement('circle',{cx:x(d.x),cy:y(d.y),r:2.7,fill:color(m.color)});svg.append(c);if(change)d3.select(c).attr('cy',prev.y(d.y)).transition().duration(240).attr('cy',y(d.y));}
 }
 const guide=svgElement('line',{'data-chart-hover-guide':'',x1:0,x2:0,y1:frame.y,y2:frame.y+frame.h,stroke:'var(--muted-foreground)','stroke-width':1,visibility:'hidden'});svg.append(guide);
 const markers=active.map(m=>{const c=svgElement('circle',{'data-chart-hover-marker':m.key,r:4,fill:color(m.color),visibility:'hidden'});svg.append(c);return{m,c};});
 const overlay=svgElement('rect',{'data-chart-hit':'','data-chart-hover-overlay':'cross-series',x:frame.x,y:frame.y,width:frame.w,height:frame.h,fill:'transparent'});svg.append(overlay);
 let pinned=false;
 function clear(){if(pinned)return;tooltip.hidden=true;guide.setAttribute('visibility','hidden');markers.forEach(({c})=>c.setAttribute('visibility','hidden'));}
 function detail(event){
  const [px]=d3.pointer(event,svg),cursor=Math.max(x(data.versions[0]),Math.min(x(data.versions.at(-1)),px)),vx=x.invert(cursor);
  const points=data.versions.map(v=>({x:v}));const nearest=d3.bisector(d=>d.x).center(points,vx);
  let a=Math.max(0,d3.bisector(d=>d.x).right(points,vx)-1),b=Math.min(points.length-1,a+1);
  const va=points[a].x,vb=points[b].x,weight=va===vb?0:(vx-va)/(vb-va);
  guide.setAttribute('x1',cursor);guide.setAttribute('x2',cursor);guide.setAttribute('visibility','visible');
  tooltip.replaceChildren();const head=document.createElement('div');head.textContent=`v${vx.toFixed(2)} 線段內插（非實測）`;head.style.fontWeight='500';tooltip.append(head);
  for(const {m,c} of markers){
   const value=data.values[va][m.key]+weight*(data.values[vb][m.key]-data.values[va][m.key]);c.setAttribute('cx',cursor);c.setAttribute('cy',y(value));c.setAttribute('visibility','visible');
   const row=document.createElement('div');row.className='tip-row';const label=document.createElement('span');label.textContent=m.label;const valueEl=document.createElement('span');valueEl.className='tabular-nums';valueEl.textContent=format(value);row.append(label,valueEl);tooltip.append(row);
  }
  if(references){const title=document.createElement('div');title.textContent='正式模型';title.style.marginTop='5px';tooltip.append(title);for(const m of active){const row=document.createElement('div');row.className='tip-row';const label=document.createElement('span');label.textContent=m.label;const v=document.createElement('span');v.className='tabular-nums';v.textContent=format(data.values.control[m.key]);row.append(label,v);tooltip.append(row);}}
  const note=document.createElement('div');note.className='text-small';note.textContent=`鄰近實測 v${points[nearest].x}：${active.map(m=>`${m.label} ${format(data.values[points[nearest].x][m.key])}`).join('；')}`;tooltip.append(note);tooltip.hidden=false;
  const rr=root.getBoundingClientRect(),sr=svg.getBoundingClientRect();const left=Math.max(0,Math.min(sr.left-rr.left+cursor+12,rr.width-tooltip.offsetWidth));
  tooltip.style.left=`${left}px`;tooltip.style.top=`${sr.top-rr.top+22}px`;
 }
 overlay.addEventListener('pointermove',e=>{if(!pinned)detail(e);});overlay.addEventListener('pointerleave',clear);
 overlay.addEventListener('pointerdown',e=>{pinned=!pinned;detail(e);});
 // Verify measured label bounds after layout; omit optional x ticks if crowded.
 const labels=[...gx.selectAll('text').nodes()].map(e=>({el:e,box:e.getBBox()}));
 for(let i=1;i<labels.length;i++){const p=labels[i-1],q=labels[i];const px=+p.el.parentElement.getAttribute('transform').match(/translate\(([^,]+)/)[1],qx=+q.el.parentElement.getAttribute('transform').match(/translate\(([^,]+)/)[1];if(px+p.box.x+p.box.width+4>qx+q.box.x&&i<labels.length-1)q.el.textContent='';}
 panel.drawn=true;
}
function update(animate=false){tooltip.hidden=true;refButton.setAttribute('aria-pressed',String(references));root.querySelectorAll('.series-key').forEach(b=>b.setAttribute('aria-pressed',String(!hidden.has(b.dataset.metric))));panels.forEach(p=>draw(p,animate));status.textContent=`${data.kind}，顯示 ${data.groups.flatMap(g=>g.metrics).filter(m=>!hidden.has(m.key)).length} 個指標；正式模型基準${references?'顯示':'隱藏'}`;}
refButton.addEventListener('click',()=>{references=!references;update(true);persist();});
const observer=new ResizeObserver(()=>update(false));panels.forEach(p=>observer.observe(p.holder));update();
})();
