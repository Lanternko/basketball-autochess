import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadFifth} from './run_defense_fifth.js';
import {summarizeFifth,compareFifth} from '../src/defense_fifth_scoreboard.js';
const root='reports/defense-fifth',fourth=label=>read('reports/defense-fourth/'+label+'-seeds.json').files.map(f=>read(f.file));
const runs={'00':loadFifth('grid-00'),'10':fourth('holdout-final'),'01':fourth('holdout-normalized'),'11':loadFifth('grid-11')};
const out={definition:'First digit rotation, second digit final league normalization. All cutoff41 and seeds20261012-31; identical player/card inputs. Each cell is scored on each team actual last41.',cells:Object.fromEntries(Object.entries(runs).map(([key,v])=>[key,summarizeFifth(v,41)])),paired:{rotationRaw:compareFifth(runs['10'],runs['00'],41),rotationNormalized:compareFifth(runs['11'],runs['01'],41),normalizationNoRotation:compareFifth(runs['01'],runs['00'],41),normalizationWithRotation:compareFifth(runs['11'],runs['10'],41)},sourceLabels:{'00':'grid-00','10':'holdout-final','01':'holdout-normalized','11':'grid-11'}};
fs.writeFileSync(root+'/four-cell.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(Object.fromEntries(Object.entries(out.cells).map(([k,v])=>[k,v.metrics]))));
