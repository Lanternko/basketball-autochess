import fs from 'node:fs/promises';

// Preserve raw NBA responses so card construction can be reproduced offline.
const season = '2025-26';
const directory = new URL('../data/benchmark-source/', import.meta.url);
await fs.mkdir(directory, {recursive:true});
async function get(name, endpoint, extra={}) {
  const query = new URLSearchParams({LeagueID:'00',Season:season,SeasonType:'Regular Season',PerMode:'Totals',MeasureType:'Base',TeamID:'0',LastNGames:'0',Month:'0',OpponentTeamID:'0',PaceAdjust:'N',PlusMinus:'N',Rank:'N',Period:'0',...extra});
  const url = `https://stats.nba.com/stats/${endpoint}?${query}`;
  const response = await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(30000)});
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`);
  const data = await response.json();
  const set = Array.isArray(data.resultSets) ? data.resultSets[0] : data.resultSets;
  if (!set?.rowSet?.length) throw new Error(`Empty ${name}`);
  await fs.writeFile(new URL(`${name}.json`,directory),JSON.stringify({url,fetchedAt:new Date().toISOString(),season,data})+'\n');
  console.log(name,set.rowSet.length);
  return set.headers.every(h=>typeof h==='string') ? set.rowSet.map(r=>Object.fromEntries(set.headers.map((h,i)=>[h,r[i]]))) : [];
}
const teams = await get('teams','leaguedashteamstats');
if (teams.length!==30) throw new Error('Expected exactly 30 teams');
await get('base','leaguedashplayerstats');
await get('advanced','leaguedashplayerstats',{MeasureType:'Advanced'});
await get('bio','leaguedashplayerbiostats');
await get('shots','leaguedashplayershotlocations',{DistanceRange:'By Zone'});
await get('defense-long','leaguedashptdefend',{DefenseCategory:'3 Pointers'});
await get('defense-rim','leaguedashptdefend',{DefenseCategory:'Less Than 6Ft'});
for (const t of teams.sort((a,b)=>a.TEAM_ID-b.TEAM_ID)) await get(`team-${t.TEAM_ID}`,'leaguedashplayerstats',{TeamID:String(t.TEAM_ID)});
