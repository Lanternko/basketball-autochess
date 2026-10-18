// Execution-only correction of a frozen artifact test. Prediction sources,
// selected c values, frozen source hashes and the freeze specification stay intact.
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {read,hash} from './defense_io.js';
const root='reports/defense-eighth/b',test='test/defense_eighth_b.js',freeze=root+'/v5-freeze.json';
const spec=read(freeze);for(const [file,h]of Object.entries(spec.sources))if(hash(file)!==h)throw Error('Frozen source changed: '+file);
const original=fs.readFileSync(test,'utf8'),old='source.models.role.offenseResidual.map(v=>v*c)',replacement='JSON.parse(JSON.stringify(source.models.role.offenseResidual.map(v=>v*c)))';
if(original.split(old).length!==2)throw Error('Expected exactly one serialized-residual assertion');
const generated='test/.defense_eighth_b_serialized.js';fs.writeFileSync(generated,original.replace(old,replacement));
execFileSync(process.execPath,[generated,'--artifacts'],{stdio:'inherit'});
for(const [file,h]of Object.entries(spec.sources))if(hash(file)!==h)throw Error('Frozen source changed during verification: '+file);
const audit={verifiedAt:new Date().toISOString(),stage:'B',predictionChanges:false,freezeHash:hash(freeze),originalTestHash:hash(test),executionTestHash:hash(generated),validatorHash:hash('scripts/validate_defense_eighth_b_serialization.js'),onlyCorrection:{before:old,after:replacement,reason:'JSON serialization canonicalizes negative zero to positive zero. Compare expected scaled residuals after the same JSON round trip as the persisted model. No numerical tolerance, prediction or calibration changes.'},originalArtifactTest:'Failed strict negative-zero comparison for c=0; not a model discrepancy.',correctedArtifactTest:'Passed all frozen source hashes, exact c=1 card/game parity, residual-only scaling,20 paired seeds and run/input hashes, prior/defense preservation, past-only calibration, FG gate and absence of blind-season data.'};
fs.writeFileSync(root+'/post-freeze-audit.json',JSON.stringify(audit,null,2)+'\n');
const md=['# 凍結後驗證補充','',
'原產物測試在c=0時因JSON負零記帳失敗：記憶體中的負係數乘0得到−0，JSON存檔後讀回為+0，嚴格比較誤判。預測、能力值、校準、c與比分均未修改。',
'','已保留原凍結規格及全部來源雜湊；另用相同JSON往返正規化預期的殘差陣列，再執行完整產物測試，全部通過。沒有放寬數值容差或略過檢查。',
'',`凍結規格SHA-256：${audit.freezeHash}。完整驗證來源、單一修正與時間見 [post-freeze-audit.json](post-freeze-audit.json)。`,
'','請以以下指令取代原報告的產物測試指令：','','```powershell','node scripts/validate_defense_eighth_b_serialization.js','node test/defense_seventh.js','```','',
'`npm run test:ability-eighth-b`也已指向此補充驗證。完成B後停下，沒有下載兩個盲測季。',''];
fs.writeFileSync(root+'/post-freeze-audit.md',md.join('\n'));
const report=root+'/closeout.md',marker='## 凍結後驗證補充';if(fs.existsSync(report)){
 let text=fs.readFileSync(report,'utf8').replace('node test/defense_eighth_b.js --artifacts','node scripts/validate_defense_eighth_b_serialization.js');
 if(!text.includes(marker))text+='\n'+marker+'\n\n原產物測試的JSON負零比較已以獨立驗證修正；凍結規格、來源與預測保持原樣。[修正說明與正確重跑指令](post-freeze-audit.md)。\n';fs.writeFileSync(report,text);
}
console.log('B frozen artifacts passed; serialization-only test correction recorded.');
