import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { TEAMS } from '../src/teams.js';
import { buildPer36Report, renderPer36Markdown } from '../src/per36_report.js';
import { percentileTeam } from '../src/benchmark_teams.js';
import { STABLE_POSSESSIONS } from '../src/calibration_presets.js';

const args = process.argv.slice(2);
const options = { n: 1000, seed: 20260908 };
let teamKey = null;
let opponentPr = 50;
let teamPr = null;
let preset = null;
for (let i = 0; i < args.length; i += 2) {
  const flag = args[i], value = args[i + 1];
  if (!value) throw new Error(`Missing value: ${flag}`);
  if (flag === '--team') teamKey = value.toUpperCase();
  else if (flag === '--n') options.n = Number(value);
  else if (flag === '--seed') options.seed = Number(value);
  else if (flag === '--pace') options.pace = Number(value);
  else if (flag === '--team-pr') teamPr = Number(value);
  else if (flag === '--preset') {
    if(value!=='stable-v1') throw new Error('Unknown preset');
    preset=value;Object.assign(options,STABLE_POSSESSIONS);
  }
  else if (flag === '--attribute-pr' || flag === '--opponent-pr') {
    opponentPr = Number(value);
    if (flag === '--opponent-pr') console.warn('Deprecated: --opponent-pr means ATTRIBUTE percentile only; use --attribute-pr. For the verified fixed-five league use --team-pr.');
  }
  else throw new Error(`Unknown option: ${flag}`);
}
if (teamKey && !TEAMS[teamKey]) throw new Error(`Unknown team: ${teamKey}`);
if (!Number.isSafeInteger(options.seed)) throw new Error('seed must be an integer');
options.opponent = percentileTeam(opponentPr);
if (teamPr!==null) {
  if (!Number.isFinite(teamPr)||teamPr<0||teamPr>100) throw new Error('Invalid team PR');
  if (args.includes('--attribute-pr')||args.includes('--opponent-pr')) throw new Error('Choose team PR or attribute PR, not both');
  const strength=JSON.parse(await fs.readFile(new URL('../reports/strength-validation.json',import.meta.url),'utf8'));
  const league=JSON.parse(await fs.readFile(new URL('../data/benchmark-league.json',import.meta.url),'utf8'));
  if (!strength.acceptance.passed) throw new Error('Strength benchmark has not passed');
  const {createHash}=await import('node:crypto');
  for (const [file,expected] of Object.entries(strength.hashes)) {
    const actual=createHash('sha256').update(await fs.readFile(new URL('../'+file,import.meta.url))).digest('hex');
    if(actual!==expected)throw new Error(`Stale strength benchmark: ${file}; rerun npm run validate:strength`);
  }
  const selected=[...strength.teams].sort((a,b)=>Math.abs(a.pr-teamPr)-Math.abs(b.pr-teamPr)||a.id-b.id)[0];
  options.opponent=league.teams.find(t=>t.id===selected.id);
  Object.assign(options,STABLE_POSSESSIONS,{leagueReboundShare:strength.rules.leagueReboundShare});
  preset='stable-v1';
  console.log(`Selected fixed-five ${league.season} ${options.opponent.name}, PR ${selected.pr.toFixed(2)}, rank uncertainty ${selected.rankInterval95.join('–')}; not full-rotation NBA PR`);
}
const reference = JSON.parse(await fs.readFile(new URL('../data/reference-seasons.json', import.meta.url), 'utf8'));
const contexts = JSON.parse(await fs.readFile(new URL('../data/league-context.json', import.meta.url), 'utf8')).contexts;
const reports = [];
for (const [key, team] of Object.entries(TEAMS)) {
  if (teamKey && key !== teamKey) continue;
  console.log(`Simulating ${key}: ${options.n} games, fatigue off...`);
  const report = buildPer36Report(team, reference.teams[key], {...options,
    ...(preset && teamPr===null ? {leagueReboundShare:contexts.find(c=>c.season===team.season&&c.type==='Regular Season').orebShare}: {})});
  reports.push(report);
  console.log(`  ${report.teamResult.pointsPer36.toFixed(1)} points / 36 min`);
}
const dir = fileURLToPath(new URL('../reports/', import.meta.url));
await fs.mkdir(dir, { recursive: true });
const stem = (teamKey ? `per36-${teamKey.toLowerCase()}` : 'per36') + (teamPr!==null?`-team-pr${teamPr}`:opponentPr===50 ? '' : `-pr${opponentPr}`) + (preset?`-${preset}`:'');
await fs.writeFile(path.join(dir, stem + '.json'), JSON.stringify(reports, null, 2) + '\n');
await fs.writeFile(path.join(dir, stem + '.md'), renderPer36Markdown(reports));
console.log(`Saved reports/${stem}.md and .json`);
