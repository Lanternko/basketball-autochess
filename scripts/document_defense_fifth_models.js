import fs from 'node:fs';
import {read,hash} from './defense_io.js';
// Repair inherited documentation/provenance labels only. Never modify fitted
// coefficients, predictions or engine-signals used by the saved simulations.
for(const k of [25,55]){
 const root='reports/defense-fifth/model-pre'+k,file=root+'/offline-model.json',r=read(file),before=hash(root+'/engine-signals.json'),tracking='data/defense-fifth-source/pre'+k+'/manifest.json';
 r.cutoff=k;r.split=`Chronological date+ID, team game index <=${k}; training requires BOTH teams before cutoff, excludes crossover and failed stints; test each defender after${k}.`;
 r.currentSignalLimitation=r.currentSignalLimitation.replaceAll('pre41','pre'+k).replaceAll('first41','first'+k).replaceAll('GP<=41','GP<='+k);
 delete r.sources['data/defense-third-source/manifest.json'];r.sources[tracking]=hash(tracking);
 r.metadataOnlyCorrection={script:'scripts/document_defense_fifth_models.js',sha256:hash('scripts/document_defense_fifth_models.js'),engineSignalsUnchanged:before,explanation:'Generated fitter already used the numeric cutoff and its specific tracking manifest; inherited first41 prose/source-list label corrected, no coefficient refit.'};
 fs.writeFileSync(file,JSON.stringify(r,null,2)+'\n');
 const md=root+'/offline-model.md';fs.writeFileSync(md,fs.readFileSync(md,'utf8').replaceAll('前41','前'+k).replaceAll('後41','截止'+k+'後').replaceAll('first41','first'+k).replaceAll('pre41','pre'+k).replaceAll('GP<=41','GP<='+k));
 if(hash(root+'/engine-signals.json')!==before)throw Error('Unexpected coefficient change');
}
console.log('Cutoff-specific model prose and consumed tracking provenance corrected; coefficients unchanged');
