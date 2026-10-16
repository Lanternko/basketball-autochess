// Refresh source-grounded season totals for the existing historical test lineups.
import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { TEAMS } from '../src/teams.js';

const IDS = { GSW: 1610612744, CLE: 1610612739, OKC: 1610612760,
  NYK: 1610612752, LAL: 1610612747 };
const statsUrl = (endpoint, season, teamId, measure, perMode) => {
  const query = new URLSearchParams({ LeagueID: '00', Season: season,
    SeasonType: 'Regular Season', PerMode: perMode, MeasureType: measure,
    TeamID: String(teamId), LastNGames: '0', Month: '0', OpponentTeamID: '0',
    PaceAdjust: 'N', PlusMinus: 'N', Rank: 'N', Period: '0' });
  return `https://stats.nba.com/stats/${endpoint}?${query}`;
};
async function get(url) {
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0',
    Referer: 'https://www.nba.com/' }, signal: AbortSignal.timeout(30000) });
  if (!r.ok) throw new Error(`NBA HTTP ${r.status}: ${url}`);
  const data = await r.json();
  const set = data.resultSets?.[0];
  if (!set?.headers || !set.rowSet?.length) throw new Error(`Empty NBA dataset: ${url}`);
  return { source: { url, fetchedAt: new Date().toISOString() },
    rows: set.rowSet.map(row => Object.fromEntries(set.headers.map((h, i) => [h, row[i]]))) };
}
const finite = (value, label) => {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error(`Missing ${label}`);
  return value;
};
const result = { schemaVersion: 1, scope: 'Existing test teams; same-team same-season regular-season totals', teams: {} };
for (const [key, team] of Object.entries(TEAMS)) {
  const id = IDS[key];
  if (!id) throw new Error(`Unknown team id: ${key}`);
  const [base, advanced, teamAdvanced] = await Promise.all([
    get(statsUrl('leaguedashplayerstats', team.season, id, 'Base', 'Totals')),
    get(statsUrl('leaguedashplayerstats', team.season, id, 'Advanced', 'Totals')),
    get(statsUrl('leaguedashteamstats', team.season, id, 'Advanced', 'PerGame')),
  ]);
  const t = teamAdvanced.rows.find(r => r.TEAM_ID === id);
  if (!t) throw new Error(`Missing team ${key}`);
  const players = team.roster.map(p => {
    const b = base.rows.find(r => r.PLAYER_NAME === p.name);
    const a = advanced.rows.find(r => r.PLAYER_ID === b?.PLAYER_ID);
    if (!b || !a) throw new Error(`Missing ${p.name} ${team.season}`);
    return { name: p.name, playerId: b.PLAYER_ID, games: finite(b.GP, 'GP'),
      minutes: finite(b.MIN, 'MIN'), usagePct: finite(a.USG_PCT, 'USG_PCT') * 100,
      totals: Object.fromEntries(['PTS','FGM','FGA','FG3M','FG3A','FTM','FTA',
        'OREB','DREB','REB','TOV','STL','BLK','AST'].map(k => [k, finite(b[k], k)])) };
  });
  result.teams[key] = { name: team.name, season: team.season, teamId: id,
    pace: finite(t.PACE, 'PACE'), offRtg: finite(t.OFF_RATING, 'OFF_RATING'),
    defRtg: finite(t.DEF_RATING, 'DEF_RATING'), players,
    sources: { base: base.source, advanced: advanced.source, team: teamAdvanced.source } };
  console.log(`${key} ${team.season}: ${players.length} players, pace ${t.PACE}`);
}
const destination = fileURLToPath(new URL('../data/reference-seasons.json', import.meta.url));
await fs.mkdir(fileURLToPath(new URL('../data/', import.meta.url)), { recursive: true });
await fs.writeFile(destination + '.tmp', JSON.stringify(result, null, 2) + '\n');
await fs.rename(destination + '.tmp', destination);
console.log('Saved data/reference-seasons.json');
