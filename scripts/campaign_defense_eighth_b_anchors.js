import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {read} from './defense_io.js';
import {runBPoint} from './run_defense_eighth_b_point.js';
const root='reports/defense-eighth/b';if(!fs.existsSync(root+'/development-rules.json'))execFileSync(process.execPath,['scripts/prepare_defense_eighth_b_rules.js'],{stdio:'inherit'});
const rules=read(root+'/development-rules.json');
for(const k of rules.cutoffs)for(const season of rules.developmentSeasons)for(const c of rules.selection.anchors.filter(c=>c!==1))await runBPoint(season,k,c);
