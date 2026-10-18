// Isolated probability fork: source role replaces FTR-derived creation
// dependence. Original probability source and all adopted imports stay intact.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href,encode=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const link=(s,file,map={})=>s.replace(/from\s+(['"])(\.\.?\/[^'"]+)\1/g,(_,q,f)=>`from ${q}${map[f]??url(path.resolve(path.dirname(file),f))}${q}`);
let probability=fs.readFileSync('src/probability_model.js','utf8').replaceAll('\r\n','\n');
const anchor='  const dependence = clamp(\n    C.CREATE_DEP_BASE + (M - selfCreation(handler)) / C.CREATE_DEP_SCALE, [0, 1]);';
if(probability.split(anchor).length!==2)throw Error('Creation dependence source anchor drift');
probability=probability.replace(anchor,'  const dependence = sourceCreationDependence(handler);');
probability=`import {creationDependence as sourceCreationDependence} from '${url('src/source_creation_dependence.js')}';\n`+link(probability,'src/probability_model.js');
const pu=encode(probability),defense=link(fs.readFileSync('src/defense_probability.js','utf8'),'src/defense_probability.js',{'./probability_model.js':pu}),du=encode(defense);
const source=link(fs.readFileSync('reports/player-impact-v28/model.mjs','utf8'),'reports/player-impact-v28/model.mjs',{'../../src/defense_probability.js':du});
const model=await import(encode(source));
export const {contestDeltas,exposureDefenseProbabilities,terminalDefenseProbabilities}=model;
