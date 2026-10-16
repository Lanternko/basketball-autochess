import {read} from './defense_io.js';
import {runBPoint} from './run_defense_eighth_b_point.js';
const root='reports/defense-eighth/b',r=read(root+'/development-rules.json'),sel=read(root+'/selection.json');
for(const k of r.cutoffs)for(const season of r.developmentSeasons)await runBPoint(season,k,sel.cutoffs[k].c);
