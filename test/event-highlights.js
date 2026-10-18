import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { TEAMS } from '../src/teams.js';
import { simulateGame } from '../src/simulation_engine.js';
import { eventHighlights } from '../src/event-highlights.js';
import { PLAYER_PORTRAITS } from '../src/player-portraits.js';
const teams=[TEAMS.GSW,TEAMS.CLE];
const {events}=simulateGame(...teams,{possessions:50,seed:20260908,replay:true});
const seen=new Set();
for (const [index,event] of events.entries()) {
 const items=eventHighlights(event,events[index-1],teams);
 for(const item of items) for(const change of item.changes) {
  seen.add(change.key);
  assert.equal(change.delta,event.players[item.side][item.player][change.key]-(events[index-1]?.players[item.side][item.player][change.key]??0));
  assert.ok(change.delta>0);
 }
 if(event.type==='STEAL') {
  assert.equal(items[0].side,1-event.off);
  assert.equal(items[0].name,teams[1-event.off].roster[event.defender].name);
  assert.equal(items[0].changes[0].key,'stl');
 }
 if(event.blocker) assert.ok(items.some(item=>item.name===event.blocker && item.changes.some(c=>c.key==='blk')));
 if(['POSSESSION','PASS'].includes(event.type)) assert.equal(items.length,0);
}
assert.deepEqual([...seen].sort(),['blk','pf','pts','reb','stl','tov']);
assert.deepEqual(eventHighlights(null,null,teams),[]);
for(const team of Object.values(TEAMS)) for(const p of team.roster) {
 assert.ok(PLAYER_PORTRAITS[p.name],`${p.name} has a portrait`);
 assert.ok(readFileSync(new URL('../'+PLAYER_PORTRAITS[p.name],import.meta.url)).length>5000);
}
console.log('Highlights: scoring/rebounds/steals/blocks/turnovers attributed correctly; all 25 portraits available.');
