const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
  for (const [w,h] of [[390,820],[300,640],[1100,800]]) { const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
    for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
    await p.click('[data-act=fight]'); await p.waitForTimeout(600);
    const pos=()=>p.evaluate(()=>{const r=document.getElementById('hand').getBoundingClientRect();return Math.round(r.top)+'/'+Math.round(document.getElementById('atkBtn').getBoundingClientRect().height)});
    const before=await pos(); for(let i=0;i<5;i++){ await p.click(`#hand .card:nth-child(${i+1})`); await p.waitForTimeout(80); }
    const after=await pos(); console.log(w,h,'hand top/btn height before',before,'after',after, await p.evaluate(()=>document.getElementById('atkBtn').textContent)); }
  await b.close(); })();
