"""Source workload and explicitly documented absence reasons, without rank fitting."""
import collections
import hashlib
import json
import math
import re
import statistics
from pathlib import Path

ROOT = Path('reports/player-impact-v29')
SEASONS = ['2022-23', '2023-24', '2024-25', '2025-26']
ROOT.mkdir(parents=True, exist_ok=True)
hashes = {}


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    hashes[path.as_posix()] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def seconds(value):
    if not value:
        return 0.
    if value.startswith('PT'):
        match = re.fullmatch(r'PT(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?', value)
        assert match, value
        h, m, s = [float(x or 0) for x in match.groups()]
        return h * 3600 + m * 60 + s
    m, s = value.split(':')
    return float(m) * 60 + float(s)


def classify(player):
    if seconds(player['statistics']['minutes']) > 0:
        return 'played'
    # Description text alone is not a medical classification. Only explicit
    # source injury/illness codes or the traditional-box comment count.
    code = player.get('notPlayingReason', '')
    comment = player.get('comment', '')
    if code in ['INACTIVE_INJURY', 'DNP_INJURY'] or re.search(r'\bInjury/Illness\b', comment, re.I):
        return 'documented_injury_illness'
    if code or comment:
        return 'other_documented_absence'
    return 'unknown_zero_minutes'


history = collections.defaultdict(dict)
leader_loads = []
season_audits = []
game_rows = []
names = {}
for season in SEASONS:
    b = read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')
    games = {g['id']: g for g in b['exposure']['games']}
    source_candidates = collections.defaultdict(list)
    for src in b['exposure']['sources']:
        p = Path(src['file'])
        if not p.exists():
            p = Path('data') / p
        raw = read(p)
        data = raw.get('data', raw)
        game = data.get('game', data.get('boxScoreTraditional'))
        if game is None:
            assert data.get('resource') == 'leaguedashteamstats', (p, list(data))
            continue  # Exposure provenance also lists its league-aggregate input.
        source_candidates[game['gameId']].append((p, game))
    seen = set()
    team_games = collections.Counter()
    team_player_games = collections.defaultdict(list)
    reasons = collections.Counter()
    source_differences = []
    players = collections.defaultdict(lambda: dict(listedGames=0, playedGames=0, starts=0,
        documentedInjuryIllnessGames=0, otherDocumentedAbsences=0, unknownZeroMinuteGames=0,
        playedMinutes=[], teamIds=set()))
    for gid, exposure in games.items():
        choices = source_candidates[gid]
        assert choices
        def mismatch(choice):
            _, game = choice
            raw_by_id = {p['personId']: p for tag in ['homeTeam', 'awayTeam'] for p in game[tag]['players']}
            return sum(abs(seconds(raw_by_id[p['playerId']]['statistics']['minutes']) - p['seconds'])
                for t in exposure['teams'] for p in t['players'])
        pth, game = min(choices, key=mismatch)
        err = mismatch((pth, game))
        # Rounded traditional boxes may differ by <=0.5 seconds/player from
        # fractional live boxes; retain differences instead of erasing them.
        if err > .001:
            source_differences.append(dict(id=gid, absoluteSecondsDifference=err))
        assert err < 60, (season, gid, err)
        raw_teams = {game[tag]['teamId']: game[tag] for tag in ['homeTeam', 'awayTeam']}
        for team in exposure['teams']:
            tid = team['teamId']
            team_games[tid] += 1
            exposure_by_id = {p['playerId']: p for p in team['players']}
            for p in raw_teams[tid]['players']:
                pid = p['personId']
                assert (gid, pid) not in seen, (gid, pid)
                seen.add((gid, pid))
                names[pid] = p.get('name') or ' '.join([p.get('firstName', ''), p.get('familyName', '')]).strip()
                row = players[pid]
                row['teamIds'].add(tid)
                row['listedGames'] += 1
                kind = classify(p)
                reasons[kind] += 1
                ep = exposure_by_id.get(pid)
                raw_sec = seconds(p['statistics']['minutes'])
                sec = ep['seconds'] if ep else raw_sec
                assert (sec > 0) == (raw_sec > 0)
                start = bool(ep['starter']) if ep else str(p.get('starter')) == '1'
                if kind == 'played':
                    row['playedGames'] += 1
                    row['starts'] += int(start)
                    row['playedMinutes'].append(sec / 60)
                    team_player_games[tid, pid].append(sec / 60)
                elif kind == 'documented_injury_illness':
                    row['documentedInjuryIllnessGames'] += 1
                elif kind == 'other_documented_absence':
                    row['otherDocumentedAbsences'] += 1
                else:
                    row['unknownZeroMinuteGames'] += 1
                game_rows.append(dict(season=season, gameId=gid, teamId=tid, playerId=pid,
                    minutes=sec / 60, starter=start, status=kind, source=pth.as_posix(),
                    reason=p.get('notPlayingReason', ''), comment=p.get('comment', '')))
    for pid, row in players.items():
        row['teamIds'] = sorted(row['teamIds'])
        row['minutesPerPlayedGame'] = statistics.mean(row['playedMinutes']) if row['playedMinutes'] else None
        row['injuryIllnessListedRate'] = row['documentedInjuryIllnessGames'] / row['listedGames']
        row['historyCoverageAdequate'] = row['listedGames'] >= max(team_games[t] for t in row['teamIds']) / 2
        assert row['listedGames'] == (row['playedGames'] + row['documentedInjuryIllnessGames']
            + row['otherDocumentedAbsences'] + row['unknownZeroMinuteGames'])
        history[pid][season] = row
    if season != '2025-26':
        for tid, ng in team_games.items():
            eligible = [(statistics.mean(ms), pid, len(ms)) for (teamid, pid), ms in team_player_games.items()
                if teamid == tid and len(ms) >= ng / 2]
            mpg, pid, gp = max(eligible)
            leader_loads.append(dict(season=season, teamId=tid, playerId=pid, games=gp, minutesPerPlayedGame=mpg))
    source_ids = {p['playerId'] for t in b['league']['teams'] for p in t['roster']}
    assert source_ids <= players.keys()
    season_audits.append(dict(season=season, games=len(games), listedPlayerGames=len(seen),
        absenceCategories=dict(reasons), players=len(players), ratedSourcePlayers=len(source_ids),
        sourceMinuteDifferences=source_differences))
    print(json.dumps(season_audits[-1] | dict(sourceMinuteDifferences=len(source_differences))), flush=True)

# Fixed before inspecting any new benchmark ranking: typical team-leading
# supported load, fitted ONLY to the three older complete seasons (90 leaders).
cap = statistics.median(x['minutesPerPlayedGame'] for x in leader_loads)
assert len(leader_loads) == 90 and 30 <= cap <= 42
players_out = {}
for pid, seasons in history.items():
    target = seasons.get('2025-26')
    if not target or not target['playedGames']:
        continue
    rates = sorted((x['injuryIllnessListedRate'] for x in seasons.values()
        if x['historyCoverageAdequate']), reverse=True)
    # Removing the worst season makes one isolated bad year exactly zero.
    # The second-highest observed season is evidence of recurrence, not a
    # clinical prognosis. Missing pre-debut years are never filled with zeros.
    persistent = rates[1] if len(rates) >= 2 else 0
    supported = statistics.mean(min(m, cap) for m in target['playedMinutes'])
    players_out[str(pid)] = dict(playerId=pid, name=names[pid], history=seasons,
        supportedMinutes=supported, workloadShare=supported / cap,
        persistentDocumentedInjuryIllnessRate=persistent,
        recurrenceSeasons=sum(x['documentedInjuryIllnessGames'] > 0 and x['historyCoverageAdequate'] for x in seasons.values()),
        # Policy coefficient, NOT a fitted clinical/causal parameter. Sensitivity
        # arms 0 / 0.05 / 0.10 are retained; primary prototype uses 0.10.
        reliabilityScale=1 - .10 * persistent,
        primaryBenchmarkMinutes=supported * (1 - .10 * persistent))

payload = dict(version='workload-availability-29', season='2025-26',
    capMinutes=cap, capTrainingLeaders=leader_loads, seasons=season_audits,
    design='Per-played-game source workload clipped before averaging; no games-missed multiplier. Cap is median team-leading MPG among players with >=half team games, 2022-25 only. All 2025-26 source players retained. Explicit injury/illness absence codes only, other/unknown absences separate. Second-highest adequately covered seasonal injury/listed-game fraction gives zero for one isolated injury season. Four-year window, limited/incomplete box listings are not complete contract or medical histories. Coefficient 0.10 is a disclosed provisional preference, not outcome-fitted; 0/0.05/0.10 sensitivity required. No changes to attributes or per36 source efficiencies.',
    players=players_out, hashes=hashes)
out = ROOT / 'workload-source.json'
assert not out.exists(), 'Preserve frozen source build'
out.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
(ROOT / 'workload-game-rows.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in game_rows), encoding='utf-8')
print(json.dumps(dict(file=str(out), capMinutes=cap, players=len(players_out), hashes=len(hashes))), flush=True)
