// Derive visual feedback from the same snapshots used by the box score.
// Never invent an attribution from the offensive handler (steals/blocks belong to defenders).
export function eventHighlights(event, previous, teams) {
  if (!event) return [];
  const metrics = [
    ['pts', '得分'], ['reb', '籃板'], ['stl', '抄截'], ['blk', '火鍋'], ['tov', '失誤'], ['pf', '犯規'],
  ];
  const highlights = [];
  event.players.forEach((rows, side) => rows.forEach((row, player) => {
    const changes = metrics.flatMap(([key, label]) => {
      const delta = row[key] - (previous?.players[side][player][key] ?? 0);
      return delta > 0 ? [{ key, label, delta, total: row[key] }] : [];
    });
    if (changes.length) highlights.push({ side, player, name: teams[side].roster[player].name, changes });
  }));
  // A successful defensive play gets the leading visual, followed by the turnover.
  return highlights.sort((a, b) => Number(a.changes[0].key === 'tov') - Number(b.changes[0].key === 'tov'));
}
