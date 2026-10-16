import fs from 'node:fs';
import {attachCreationContext} from '../../src/measured_creation_context.js';
import {ovrInput as previousInput} from '../player-impact-v6/ovr-input.mjs';
import {attachMeasurements} from './input.mjs';
export function ovrInput(){const x=previousInput();attachMeasurements(x.players,'2025-26');for(const t of x.opponents)attachMeasurements(t.roster,'2025-26');attachCreationContext(x.profiles,JSON.parse(fs.readFileSync('reports/player-impact-v13/2025-26-contexts.json')).contextReference);return x;}
