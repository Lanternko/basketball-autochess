const {chromium}=require('C:/Users/柯子捷/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('node:path'),fs=require('node:fs');
(async()=>{
 console.log('browser',chromium.executablePath());
 let browser;try{browser=await chromium.launch({headless:true});}catch(e){console.log('default browser unavailable; trying Edge');browser=await chromium.launch({headless:true,channel:'msedge'});}
 const results=[];
 for(const name of ['ovr-evolution','personal-error-curves','team-error-curves']){
  const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file:///'+path.resolve('reports/model-evolution-20261016/'+name+'.preview.html').replaceAll('\\','/'));
  const frame=page.frameLocator('iframe');await frame.locator('svg').first().waitFor({timeout:30000});
  await page.waitForTimeout(500);
  for(const width of [736,360,320]){
   await page.setViewportSize({width:width+40,height:1000});
   // Match the actual host width inside the standalone preview iframe.
   await page.locator('iframe').evaluate((e,w)=>{e.style.width=w+'px';},width);
   await page.waitForTimeout(120);
   const state=await frame.locator('body').evaluate(body=>({width:body.clientWidth,scroll:body.scrollWidth,svgs:body.querySelectorAll('svg').length,charts:[...body.querySelectorAll('svg')].map(s=>({viewBox:s.getAttribute('viewBox'),width:s.getBoundingClientRect().width})),text:body.textContent.slice(0,200)}));
   if(state.scroll>state.width+2)throw Error(name+' horizontal overflow '+JSON.stringify(state));
   results.push({name,width,state,errors:[...errors]});
   if(width===736){const h=await frame.locator('body').evaluate(b=>b.scrollHeight);await page.locator('iframe').evaluate((e,h)=>{e.style.maxHeight='none';e.style.minHeight='0';e.style.height=h+'px';},h+10);await page.setViewportSize({width:width+40,height:h+100});await frame.locator('body').screenshot({path:path.resolve(`reports/model-evolution-20261016/${name}.png`)});}
  }
  if(name!=='ovr-evolution'){
   const key=frame.locator('.reference-key');await key.click();if(await key.getAttribute('aria-pressed')!=='false')throw Error('reference toggle failed');
   const metric=frame.locator('.series-key').first();await metric.click();if(await metric.getAttribute('aria-pressed')!=='false')throw Error('metric toggle failed');
   await metric.click();await key.click();
   const overlay=frame.locator('[data-chart-hover-overlay]').first();await overlay.hover();if(!await frame.locator('.curve-tooltip').isVisible())throw Error('hover failed');
  }
  if(errors.length)throw Error(name+' script errors '+JSON.stringify(errors));await page.close();
 }
 await browser.close();fs.writeFileSync('reports/model-evolution-20261016/visual-verification.json',JSON.stringify({passed:true,results},null,2));console.log('PASS: three charts, 736/360/320px, controls, hover, no script errors.');
})().catch(e=>{console.error(e);process.exitCode=1;});
