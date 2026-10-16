import {runFifth} from './run_defense_fifth.js';
import {fifthFinalOptions} from '../src/defense_fifth_clock.js';
const cutoff=Number(process.argv[2]??41);
await runFifth('fifth-final-'+cutoff,{cutoff,options:fifthFinalOptions(cutoff)});
