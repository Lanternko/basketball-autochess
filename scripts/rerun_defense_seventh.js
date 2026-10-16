import {read} from './defense_io.js';
import {runSeventh} from './run_defense_seventh.js';
const label=process.argv[2],m=read('reports/defense-seventh/'+label+'-seeds.json');
if(!m.extra)throw Error('Use run_defense_seventh_preseason.js for per-seed preseason bundles');
await runSeventh(label,m.extra,m.files.map(f=>f.seed));
