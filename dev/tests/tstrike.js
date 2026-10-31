const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const [w,h,n] of [[1440,900,'S'],[390,844,'Q']]){
const p=await b.newPage({viewport:{width:w,height:h}});
await p.goto('http://localhost:8765/site/index.html');await p.waitForTimeout(1500);
await p.evaluate(()=>document.getElementById('ambushAt').scrollIntoView()); await p.evaluate(()=>scrollBy(0,-innerHeight*0.5)); await p.waitForTimeout(1200); await p.screenshot({path:`/tmp/claude-0/${n}amb.png`});
await p.evaluate(()=>{const s=document.getElementById('stage');s.scrollIntoView({block:'center'})}); await p.waitForTimeout(1000); await p.screenshot({path:`/tmp/claude-0/${n}k1.png`});
await p.waitForTimeout(2000); await p.screenshot({path:`/tmp/claude-0/${n}k2.png`});
await p.goto('http://localhost:8765/site/index.html');await p.waitForTimeout(2500);await p.screenshot({path:`/tmp/claude-0/${n}hero.png`});
await p.evaluate(()=>document.getElementById('try').scrollIntoView()); await p.waitForTimeout(1800); await p.screenshot({path:`/tmp/claude-0/${n}try.png`});}
await b.close();})();
