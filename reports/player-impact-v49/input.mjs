import fs from 'node:fs';
import {loadInput as previous} from '../player-impact-v47/input.mjs';
export function loadInput(season){const b=previous(season);b.options.rotationPolicy='measured';b.options.measuredRotationProfiles=JSON.parse(fs.readFileSync(`reports/player-impact-v49/${season}-profiles.json`));return b;}
