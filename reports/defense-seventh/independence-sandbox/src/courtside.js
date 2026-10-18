import { TEAMS } from './teams.js';
import { simulateGame } from './simulation_engine.js';
import { PLAYER_PORTRAITS } from './player-portraits.js';
import { eventHighlights } from './event-highlights.js';
import { CourtMotion } from './court-motion.js';
import { playerFigure } from './player-figure.js';
import { planScene, sampleScene, replayRemaining } from './court-scene.js';
import { motionKind, actionLabel, spacePositions } from './motion-model.js';
const $ = id => document.getElementById(id);
const portrait = name => `<span class="portrait ${PLAYER_PORTRAITS[name]?.endsWith('.jpg') ? 'portrait-photo' : ''}"><img src="${PLAYER_PORTRAITS[name]}" alt="${name} 的照片" draggable="false" decoding="async"></span>`;
// Local assets keep portraits available during playback without a third-party request.
document.addEventListener('error', event => {
  if (event.target.matches?.('.portrait img')) event.target.parentElement.classList.add('photo-unavailable');
}, true);
let highlightCursor = -1;
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
function renderHighlights(animate = false) {
  if (!eventResolved) { document.querySelectorAll('.stat-pop').forEach(n=>n.remove()); highlightCursor=-1; return; }
  if (highlightCursor===cursor) return;
  highlightCursor=cursor;
  document.querySelectorAll('.stat-pop').forEach(n=>n.remove());
  for(const item of eventHighlights(current(),cursor>1?game.events[cursor-2]:null,teams)) {
    const token=$('tokens').querySelector(`[data-side="${item.side}"][data-player="${item.player}"]`);
    const cue=document.createElement('span');
    cue.className='stat-pop'+(animate&&!reducedMotion.matches?' arriving':'');
    cue.setAttribute('aria-hidden','true');
    cue.textContent=item.changes.map(c=>`${c.label} +${c.delta}`).join(' · ');
    token.append(cue);
  }
}

const keys = Object.keys(TEAMS);
for (const id of ['teamA','teamB']) $(id).innerHTML = keys.map(key => `<option value="${key}">${TEAMS[key].name}</option>`).join('');
$('teamA').value = 'GSW'; $('teamB').value = 'CLE';
let teams, game, cursor = 0, playing = false, side = 0, selected = 0, seed = 20260908;
const zero = () => ({pts:0,reb:0,stl:0,blk:0,fgm:0,fga:0,fg3m:0,fg3a:0,ftm:0,fta:0,tov:0,pf:0});
const current = () => cursor ? game.events[cursor-1] : null;
let eventResolved = true;
let frames=[], durations=[];
const motion = new CourtMotion();
const viewed = () => eventResolved ? current() : cursor > 1 ? game.events[cursor - 2] : null;
const stats = () => viewed()?.players ?? teams.map(t => t.roster.map(zero));
function describe(e) {
  const name=teams[e.off].roster[e.player].name;
  if(e.type==='POSSESSION') return `${name} · 持球推進`;
  if(e.type==='PASS') return `${teams[e.off].roster[e.from].name} → ${name}`;
  if(e.type==='STEAL') return `${teams[1-e.off].roster[e.defender].name} · 抄截 +1`;
  if(e.type==='TOV') return `${name} · 失誤 +1`;
  if(['OREB','DREB'].includes(e.type)) return `${name} · ${e.type==='OREB'?'進攻':'防守'}籃板 +1`;
  if(e.type==='FOUL') return `${teams[1-e.off].roster[e.defender].name} · 犯規 +1，${e.attempts} 次罰球`;
  if(e.type.startsWith('FT')) return `${name} · 罰球 ${e.attempt}/${e.attempts} ${e.type==='FTM'?'命中 +1':'未進'}`;
  if(e.blocker) return `${e.blocker} · 火鍋 +1`;
  return `${name} · ${motionKind(e,teams)==='dunk'?'灌籃':e.type.startsWith('FG3')?'三分':e.type.startsWith('MID')?'中距離':'上籃'}${e.type.endsWith('M')?`命中 +${e.type.startsWith('FG3')?3:2}`:'未進'}`;
}
function buildTokens() {
  $('tokens').innerHTML=teams.map((team,s)=>team.roster.map((p,i)=>`<div class="token ${s?'away-token':''}" data-side="${s}" data-player="${i}"><button aria-label="追蹤 ${p.name}">${playerFigure(i+1)}</button><span class="name">${p.name.split(' ').at(-1)}</span></div>`).join('')).join('');
  for(const token of $('tokens').children) token.querySelector('button').onclick=()=>{side=+token.dataset.side;selected=+token.dataset.player;render();};
  teams.forEach((team,s)=>{
    const root=$(s?'lineupB':'lineupA');
    root.innerHTML=team.roster.map((p,i)=>`<button class="lineup-player" data-player="${i}" aria-label="追蹤 ${p.name}" aria-pressed="false">${portrait(p.name)}<span><span class="position">${p.pos} · ${i+1}</span><strong>${p.name.split(' ').at(-1)}</strong><small class="live-stats">0 分 · 0 板</small></span></button>`).join('');
    for(const card of root.children) card.onclick=()=>{side=s;selected=+card.dataset.player;render();};
  });
}
function positions(e) {
  const off = e ? (['DREB'].includes(e.type) ? 1-e.off : e.off) : 0;
  const base = [[57,50],[69,18],[69,82],[82,34],[85,67]];
  const order = { PG:0, SG:1, SF:2, PF:3, C:4 };
  const all = [0,1].map(s => teams[s].roster.map((p,i) => {
    const slots = teams[s].roster.map((p,index) => ({index,rank:order[p.pos] ?? 2}))
      .sort((a,b) => a.rank-b.rank);
    let [x,y] = base[slots.findIndex(slot => slot.index===i)];
    if (s !== off) { x += 6; y += y<50 ? -10 : 10; }
    return [off===0 ? x : 100-x,y];
  }));
  if (e && /^(FG3|MID|RIM|FOUL|FT)/.test(e.type)) {
    const x = e.type.startsWith('FG3') ? 66 : e.type.startsWith('MID') ? 79 : e.type==='FOUL' || e.type.startsWith('FT') ? 78 : 88;
    const y = e.type.startsWith('FG3') ? (e.player%2 ? 28 : 74) : e.type.startsWith('MID') ? 39 : 50;
    all[e.off][e.player] = [e.off===0 ? x : 100-x,y];
    all[1-e.off][e.player] = [e.off===0 ? x+7 : 93-x,y-7];
  }
  if (e?.type.startsWith('FT')) {
    all[e.off][e.player] = [e.off===0 ? 78 : 22,50];
    const teammates = all[e.off].map((_,i)=>i).filter(i=>i!==e.player);
    teammates.forEach((i,n)=>{ all[e.off][i]=[e.off===0 ? 83+(n%2)*5 : 17-(n%2)*5,n<2?34:66]; });
    all[1-e.off] = [[86,40],[86,60],[91,35],[91,65],[62,77]].map(([x,y])=>[e.off===0?x:100-x,y]);
  }
  if (e && ['OREB','DREB'].includes(e.type)) all[e.off][e.player] = [off===0 ? 88 : 12,54];
  if (e && motionKind(e, teams)==='dunk') {
    all[e.off][e.player]=[e.off===0?89.2:10.8,54];
    all[1-e.off][e.player]=[e.off===0?82:18,58];
  }
  return spacePositions(all, e ? [e.off,e.player] : null, 5.5).map(row=>row.map(([x,y])=>[x,Math.max(21,Math.min(86,y))]));
}
function renderCourt() {
  for (const token of $('tokens').children) token.classList.toggle('selected',+token.dataset.side===side && +token.dataset.player===selected);
}
function render(animateHighlights = false) {
  const e=current(), rows=stats()[side], ended=cursor===game.events.length && eventResolved && motion.finished;
  $('scoreA').textContent=viewed()?.score[0] ?? 0; $('scoreB').textContent=viewed()?.score[1] ?? 0;
  $('matchStatus').textContent=ended ? `比賽結束 · ${game.tie ? '平手' : teams[game.winnerA ? 0 : 1].name+' 獲勝'}` : e ? `第 ${e.poss+1} / ${game.possessions} 次進攻 · 尚餘 ${game.possessions-e.poss-1} 次` : '準備開賽 · 每隊 50 次進攻';
  $('play').textContent=playing ? 'Ⅱ 暫停' : ended ? '↺ 再看一次' : '▶ 播放';
  $('step').disabled=cursor===game.events.length;
  $('courtStatus').textContent=ended ? '終場' : e ? `${teams[e.type==='FOUL'||e.type==='STEAL'||e.blocker?1-e.off:e.off].name} · ${actionLabel(e,motionKind(e,teams))}` : '等待開球';
  $('eventCaption').textContent=`追蹤 ${teams[side].roster[selected].name}`;
  $('announcement').textContent=e ? eventResolved ? describe(e) : `${e.type==='FOUL' ? teams[1-e.off].roster[e.defender].name : e.blocker ?? teams[e.off].roster[e.player].name} · ${actionLabel(e,motionKind(e,teams))}…` : '球員就位，等待開球。';
  $('feed').innerHTML=game.events.slice(Math.max(0,cursor-35),cursor-(eventResolved?0:1)).reverse().map(ev => `<li><small>第 ${ev.poss+1} 次進攻 · ${ev.score.join(' : ')}</small>${describe(ev)}</li>`).join('');
  $('seek').value=cursor; $('progress').textContent=`${cursor} / ${game.events.length}`;
  $('tabA').setAttribute('aria-pressed',side===0); $('tabB').setAttribute('aria-pressed',side===1);
  teams.forEach((team,s)=>{
    for(const card of $(s?'lineupB':'lineupA').children){
      const i=+card.dataset.player,r=stats()[s][i];
      card.setAttribute('aria-pressed',s===side&&i===selected);
      card.querySelector('.live-stats').textContent=`${r.pts} 分 · ${r.reb} 板`;
    }
  });
  $('stats').innerHTML=teams[side].roster.map((p,i)=>{const r=rows[i];return `<tr><td><span>${p.pos}</span>${p.name}</td><td>${r.pts}</td><td>${r.reb}</td><td>${r.stl}</td><td>${r.blk}</td><td>${r.fgm}/${r.fga}</td><td>${r.fg3m}/${r.fg3a}</td><td>${r.ftm}/${r.fta}</td><td>${r.tov}</td><td>${r.pf ?? 0}</td></tr>`;}).join('');
  renderCourt();
  renderHighlights(animateHighlights);
  updateClock(motion.progress);
}
function updateClock(progress=1){
  const seconds=Math.ceil(replayRemaining(durations,cursor,progress)/1000);
  $('replayClock').textContent=`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;
}
function present(animate = false) {
  eventResolved=!animate;
  render();
  motion.start({event:current(),positions:positions(current()),teams,animate,
    frame:cursor?frames[cursor-1]:null,nextEvent:game.events[cursor],
    onFrame:updateClock,
    onImpact:()=>{eventResolved=true;render(true);},
    onComplete:()=>{
      if(playing && cursor<game.events.length) {
        // Yield even in reduced-motion mode: never recurse through a whole game.
        const generation=motion.generation;
        requestAnimationFrame(()=>{if(playing&&generation===motion.generation)advance();});
      } else {playing=false;render();}
    },
  });
}
function pause(){ playing=false;motion.pause(); }
function advance(){ if(cursor<game.events.length){ cursor++;present(true); } }
function load(){
  pause();teams=[TEAMS[$('teamA').value],TEAMS[$('teamB').value]];
  game=simulateGame(...teams,{possessions:50,seed,replay:true});cursor=0;selected=0;highlightCursor=-1;
  $('seek').max=game.events.length;buildTokens();
  frames=[sampleScene(planScene(null,null,positions(null),teams),1)];durations=[];
  game.events.forEach((event,i)=>{
    const scene=planScene(event,frames[i],positions(event),teams,game.events[i+1]);
    frames.push(sampleScene(scene,1));durations.push(scene.duration);
  });
  present();
}
$('play').onclick=()=>{
  if(playing){pause();render();return;}
  playing=true;
  if(cursor===game.events.length && motion.finished){cursor=0;highlightCursor=-1;}
  if(motion.finished) advance();else motion.resume();
  render();
};
$('step').onclick=()=>{pause();advance();};
$('reset').onclick=()=>{pause();cursor=0;present();};
$('new').onclick=()=>{seed++;load();};
$('speed').onchange=()=>motion.setSpeed(Number($('speed').value));
$('seek').oninput=()=>{pause();cursor=Number($('seek').value);present();};
$('teamA').onchange=load;$('teamB').onchange=load;
$('tabA').onclick=()=>{side=0;render();};$('tabB').onclick=()=>{side=1;render();};
$('detailsToggle').onclick=()=>{
  const open=$('matchDetails').hidden;
  $('matchDetails').hidden=!open;$('detailsToggle').setAttribute('aria-expanded',open);
  $('detailsToggle').textContent=open?'收起數據 ↑':'數據與紀錄 ↓';
};
$('fullscreen').onclick=async()=>{
  try {if(document.fullscreenElement)await document.exitFullscreen();else await document.querySelector('.broadcast').requestFullscreen();}
  catch {$('announcement').textContent='目前瀏覽器未提供全螢幕，請使用視窗觀賽。';}
};
new ResizeObserver(()=>motion.resize()).observe($('court'));
load();
