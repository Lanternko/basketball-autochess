import fs from 'node:fs';import crypto from 'node:crypto';
const root='reports/defense-tenth/step4-t2',p=JSON.parse(fs.readFileSync(root+'/measurement-supplement.json')),sources=[],failures=[];
await Promise.all(p.urls.map(async(url)=>{const season=/news\/(\d{4}-\d{2})/.exec(url)[1],file=root+'/raw/'+season+'/trade-tracker.html';try{let html;
  if(fs.existsSync(file))html=fs.readFileSync(file,'utf8');else{const r=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(25000)});if(!r.ok)throw Error('HTTP '+r.status);html=await r.text();if(!html.includes('Trade Tracker'))throw Error('Wrong page');fs.writeFileSync(file,html);}
  sources.push({season,url,file,sha256:crypto.createHash('sha256').update(html).digest('hex')});
}catch(e){failures.push({season,url,error:String(e)});}}));
fs.writeFileSync(root+'/trade-sources.json',JSON.stringify({sources,failures},null,2)+'\n');console.log('Trade sources',sources.length,'failures',failures);
