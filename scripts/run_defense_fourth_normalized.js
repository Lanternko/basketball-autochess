import fs from 'node:fs';
import {read} from './defense_io.js';
import {runLabel,loadRuns} from './run_defense_fourth.js';
import {comparison} from '../src/defense_fourth_scoreboard.js';
const root='reports/defense-fourth',selection=read(root+'/final-selection.json');
const options={...selection.finalOptions,...read(root+'/normalization-full.json').selected};
const rawFinalLabel=selection.rawFinalLabel??selection.finalLabel;
const result=await runLabel('final-normalized',options),rawDelta=comparison(result,loadRuns(rawFinalLabel));
// League accounting corrections are not selected by accuracy; preserve the raw comparison.
const updated={...selection,rawFinalLabel,finalLabel:'final-normalized',finalOptions:options,leagueNormalizationDelta:rawDelta};
fs.writeFileSync(root+'/final-selection.json',JSON.stringify(updated,null,2)+'\n');
const pre=read(root+'/normalization-pre41.json').selected;
await runLabel('holdout-normalized',{...selection.finalOptions,...pre},{post41:true});
updated.rawHoldoutLabel='holdout-final';updated.holdoutFinalLabel='holdout-normalized';fs.writeFileSync(root+'/final-selection.json',JSON.stringify(updated,null,2)+'\n');
