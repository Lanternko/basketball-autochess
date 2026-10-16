// v53 engine: the v47 engine with its probability model swapped for v53/model.mjs.
// No game-loop change; with no pressureMeasurement and spread scale 1 it is exactly v47.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const cache = new Map();
export async function impactEngine(version, options = {}) {
  const key = JSON.stringify([version, options]); if (cache.has(key)) return cache.get(key);
  let s = fs.readFileSync('reports/player-impact-v47/engine.mjs', 'utf8');
  const from = "url('reports/player-impact-v47/model.mjs')", to = "url('reports/player-impact-v53/model.mjs')";
  if (s.split(from).length !== 2) throw Error('v53 model anchor drift');
  s = s.replace(from, to);
  const mod = await import('data:text/javascript;base64,' + Buffer.from(s).toString('base64'));
  const run = await mod.impactEngine(version, options); cache.set(key, run); return run;
}
