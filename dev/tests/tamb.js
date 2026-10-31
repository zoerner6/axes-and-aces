const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:390,height:844}});
await p.goto('http://localhost:8765/site/index.html');await p.waitForTimeout(1500);
for(let y=0;y<9000;y+=150){ await p.mouse.wheel(0,150); await p.waitForTimeout(60);
  const on=await p.evaluate(()=>document.getElementById('amb').classList.contains('on')); if(on){ console.log('ambush at',y, await p.evaluate(()=>scrollY)); await p.waitForTimeout(700); await p.screenshot({path:'/tmp/claude-0/pamb.png'}); break; } }
await b.close();})();
