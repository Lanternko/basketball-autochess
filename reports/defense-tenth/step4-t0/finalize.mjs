// Reproducible presentation-only finalization; estimates read from immutable
// analysis/joint outputs. No model, score, selection or uncertainty changes.
import fs from 'node:fs';
import {read} from '../../../scripts/defense_io.js';
const d='reports/defense-tenth/step4-t0',a=read(d+'/analysis.json'),j=read(d+'/joint-intervals.json'),f=x=>x.toFixed(3),ci=x=>f(x.point)+' ['+x.joint95.map(f).join(', ')+']';
for(const file of ['report.md','failures.md','team-errors.md']){
 let s=fs.readFileSync(d+'/'+file,'utf8');
 s=s.replaceAll('python reports/defense-tenth/step4-t0/bootstrap.py','python -X utf8 reports/defense-tenth/step4-t0/bootstrap.py');
 s=s.replaceAll('node reports/defense-tenth/step4-t0/report.mjs','node reports/defense-tenth/step4-t0/render-adapter.mjs\nnode reports/defense-tenth/step4-t0/report-v2.mjs');
 if(!s.includes('node reports/defense-tenth/step4-t0/finalize.mjs'))s=s.replace('node reports/defense-tenth/step4-t0/audit.mjs','node reports/defense-tenth/step4-t0/finalize.mjs\nnode reports/defense-tenth/step4-t0/audit.mjs');
 for(const [x,y]of [['胜','勝'],['真实','真實'],['与','與'],['纯','純'],['场','場'],['战术','戰術'],['换','換']])s=s.replaceAll(x,y);
 fs.writeFileSync(d+'/'+file,s);
}
let s=fs.readFileSync(d+'/report.md','utf8');
if(!s.includes('## 純卡的聯盟均值漂移與來源差異'))s+='\n## 純卡的聯盟均值漂移與來源差異\n\n歷史三季關閉訊號後的效率偏差為−3.788／−3.620／−3.373分／百回合，球權偏差+1.330／+1.267／+1.435場均。這是共用v3校正常數後移除訊號的結果，沒有對純卡另校正；本次如實保留，不把去均值net誤差與聯盟合計對齊混為一談。2025–26原凍結卡的純卡效率偏差−0.280、球權+0.107。不能把歷史與2025–26當作資料來源完全一致的產物。\n\n歷史box以逐場player-game logs合計，分鐘含逐場四捨五入；2025–26原卡沿用原官方全季snapshot。上述41.1秒案例只修正零分母，不普遍更換分鐘或改卡。歷史個人卡不是舊calendar55卡，也沒有用v4殘差。\n\nbootstrap.py在Windows預設cp950下讀中文protocol失敗；重跑使用python -X utf8，程式與重抽規則不變。report.mjs一處模板字串結尾引號錯誤，原登記檔保留，render-adapter.mjs另產report-v2.mjs只修該引號；文字排版／重跑命令修正沒有修改analysis或joint-intervals。\n';
if(!s.includes('## 六項指標與聯合95%區間')){
 s+='\n## 六項指標與聯合95%區間（版本本身）\n\n| 球季 | 版本 | net RMSE | Spearman | 勝場 MAE（參考） | 勝場 RMSE（參考） | 校準斜率 | SD 比 |\n|---|---|---:|---:|---:|---:|---:|---:|\n';
 for(const c of a.cells){const v=j.comparisons[c.season].versions[c.version];s+='| '+c.season+' | '+c.version+' | '+['netRMSE','Spearman','winsMAE','winsRMSE','calibrationSlope','SDRatio'].map(k=>ci(v[k])).join(' | ')+' |\n';}
 s+='\n四季等權合併：純卡net RMSE '+f(j.comparisons['four-seasons-equal'].versions.pure.netRMSE.point)+'、v3 '+f(j.comparisons['four-seasons-equal'].versions.v3.netRMSE.point)+'；純卡−v3='+ci(j.comparisons['four-seasons-equal'].pureMinusV3.netRMSE)+'。這是同季已看過答案的模式內差異，不能作跨季或換隊能力結論。\n';
}
fs.writeFileSync(d+'/report.md',s);console.log('Finalized presentation, metrics unchanged');
