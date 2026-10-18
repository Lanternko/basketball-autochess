import fs from 'node:fs';
const original=fs.readFileSync('reports/player-impact-v6/engine.mjs','utf8'),anchor="url('reports/player-impact-v6/model.mjs')";
if(original.split(anchor).length!==2)throw Error('Accelerator model anchor drift');
const source=original.replace(anchor,"url('reports/player-impact-validation/fast-model.mjs')");
export const impactEngine=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).impactEngine;
