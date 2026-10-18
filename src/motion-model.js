// Presentation-only action selection. The model still decides every outcome.
export function motionKind(event, teams) {
  if (!event) return 'idle';
  if (event.type === 'FOUL') return 'foul';
  if (event.type.startsWith('FT')) return 'freeThrow';
  if (event.blocker) return 'block';
  if (['OREB', 'DREB'].includes(event.type)) return 'rebound';
  if (event.type === 'STEAL') return 'steal';
  if (event.type === 'PASS') return 'pass';
  if (event.type === 'TOV') return 'turnover';
  const p = teams[event.off].roster[event.player];
  if (event.type === 'RIMM' && p.physique >= 75 && p.short >= 85 && (event.poss + event.player) % 3 !== 0) return 'dunk';
  if (event.type.startsWith('RIM')) return 'layup';
  if (/^(FG3|MID)/.test(event.type)) return 'shot';
  return 'handle';
}
export function actionLabel(event, kind) {
  return { idle:'等待開球', handle:'組織進攻', pass:'傳球', shot:event?.type.startsWith('FG3') ? '三分跳投' : '中距離跳投',
    layup:'籃下終結', dunk:'戰斧劈扣', rebound:event?.type === 'OREB' ? '進攻籃板' : '防守籃板',
    block:'封阻出手', steal:'攔截傳球', turnover:'持球失誤', foul:'投籃犯規',
    freeThrow:`罰球 ${event?.attempt ?? 1} / ${event?.attempts ?? 2}` }[kind];
}
export const motionDuration = kind => ({ idle:900, handle:3200, pass:1250, shot:2400, layup:2200,
  dunk:2450, rebound:1850, block:2350, steal:1700, turnover:1500, foul:2200, freeThrow:2300 })[kind];
export const impactPoint = kind => ({ shot:.73, layup:.73, dunk:.68, block:.57, rebound:.53,
  steal:.52, foul:.4, freeThrow:.73, turnover:.45, pass:.62, handle:.2, idle:0 })[kind];
export const clamp = (n, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, n));
export const mix = (a,b,t) => a.map((v,i) => v+(b[i]-v)*t);
export const ease = t => 1-(1-clamp(t))**3;
export function arcPoint(start, end, t, height = 23) {
  const control = [(start[0]+end[0])/2, Math.max(7,Math.min(start[1],end[1])-height)];
  return start.map((v,i) => (1-t)**2*v + 2*(1-t)*t*control[i] + t*t*end[i]);
}
export function ballDestination(event, positions, kind) {
  if (!event) return [50,50];
  const hoop = [event.off===0 ? 91.2 : 8.8,50];
  if (kind === 'block') return [hoop[0] + (event.off===0 ? -10 : 10), 63];
  if (['shot','layup','freeThrow','dunk'].includes(kind)) {
    return event.type.endsWith('M') ? [hoop[0],54] : [hoop[0]+(event.off===0 ? -6 : 6),60];
  }
  const s=kind==='steal' ? 1-event.off : event.off;
  const i=kind==='steal' ? event.defender : event.player;
  return [positions[s][i][0]+2,positions[s][i][1]];
}

// Keep circles readable when a shooter moves into a teammate's default slot.
// This is presentation spacing only; it cannot affect the probability model.
export function spacePositions(positions, pinned = null, minimum = 6.6) {
  const result=positions.map(row=>row.map(p=>[...p]));
  const ids=result.flatMap((row,s)=>row.map((_,i)=>[s,i]));
  for(let pass=0;pass<12;pass++) for(let a=0;a<ids.length;a++) for(let b=a+1;b<ids.length;b++) {
    const [sa,ia]=ids[a],[sb,ib]=ids[b],pa=result[sa][ia],pb=result[sb][ib];
    let dx=pb[0]-pa[0],dy=(pb[1]-pa[1])*.54;
    const distance=Math.hypot(dx,dy);
    if(distance>=minimum) continue;
    if(distance<.01){dx=1;dy=.5;}
    const norm=Math.hypot(dx,dy),push=(minimum-distance+.05);
    const fixedA=pinned?.[0]===sa&&pinned?.[1]===ia, fixedB=pinned?.[0]===sb&&pinned?.[1]===ib;
    const wa=fixedA?0:fixedB?1:.5,wb=fixedB?0:fixedA?1:.5;
    pa[0]=clamp(pa[0]-dx/norm*push*wa,7,93);pa[1]=clamp(pa[1]-dy/norm*push*wa/.54,10,88);
    pb[0]=clamp(pb[0]+dx/norm*push*wb,7,93);pb[1]=clamp(pb[1]+dy/norm*push*wb/.54,10,88);
  }
  return result;
}
