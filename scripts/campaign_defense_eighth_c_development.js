import {execFileSync} from 'node:child_process';
import {verifyC,runCVersion} from './run_defense_eighth_c_versions.js';
const p=verifyC();for(const k of p.cutoffs)for(const v of ['v1','v3-signals-off'])await runCVersion('2025-26',k,v);
for(const s of p.developmentSeasons)execFileSync(process.execPath,['scripts/diagnose_defense_eighth_c_ablation.js',s],{stdio:'inherit'});
