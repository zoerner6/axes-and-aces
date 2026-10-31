const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
  for (const [w,h] of [[250,700],[300,640],[390,700],[390,820],[1100,700],[1100,900],[1400,650],[800,560]]) { const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true')}catch(e){} });
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
    for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
    await p.click('[data-act=fight]'); await p.waitForTimeout(600);
    const r=await p.evaluate(()=>({sh:document.documentElement.scrollHeight, stage:document.getElementById('monsterBox').getBoundingClientRect().height}));
    console.log(w,h,'page',r.sh,'stage',Math.round(r.stage), r.sh>h?'SCROLLS':'ok');
    if(w===390&&h===700) await p.screenshot({path:'w_390.png'}); }
  await b.close(); })();
