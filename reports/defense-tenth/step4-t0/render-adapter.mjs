// Fix one mismatched template-string terminator in the presentation generator.
// Preserve original registered file, all analytical programs and outputs.
import fs from 'node:fs';
import crypto from 'node:crypto';
const d='reports/defense-tenth/step4-t0',tick=String.fromCharCode(96);
const source=fs.readFileSync(d+'/report.mjs','utf8'),needle="歸因不免除失敗。','',"+tick+'登記',replacement='歸因不免除失敗。'+tick+",'',"+tick+'登記';
if(source.split(needle).length!==2)throw Error('Expected exactly one presentation syntax repair');
const code=source.replace(needle,replacement);fs.writeFileSync(d+'/report-v2.mjs',code);
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
fs.writeFileSync(d+'/render-code-registration.json',JSON.stringify({registeredAt:new Date().toISOString(),scope:'Presentation syntax only, after scoring; no changed statistics/rules/ranks/intervals',original:{file:d+'/report.mjs',sha256:sha(source)},corrected:{file:d+'/report-v2.mjs',sha256:sha(code)},repair:'One mismatched template-string terminator'},null,2)+'\n');
