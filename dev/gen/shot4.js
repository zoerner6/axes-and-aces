const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
  for (const [w,h,tag] of [[1100,860,'d'],[390,800,'p'],[300,700,'n']]) {
    const p = await b.newPage({ viewport: { width: w, height: h } }); const errs=[]; p.on('pageerror', e=>errs.push(e.message));
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(2500);
    await p.screenshot({ path: `t_${tag}_story.png` });
    if(tag!=='n'){ await p.click('[data-act=storyNext]'); await p.waitForTimeout(2500); await p.screenshot({ path: `t_${tag}_story2.png` }); }
    await p.evaluate(()=>{ document.querySelector('[data-act=storyNext]'); });
    for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(400);} }
    await p.screenshot({ path: `t_${tag}_intro.png` });
    await p.click('[data-act=fight]'); await p.waitForTimeout(600); await p.click('.skip').catch(()=>{}); await p.waitForTimeout(900);
    await p.screenshot({ path: `t_${tag}_fight.png` });
    if(tag==='p'){ await p.evaluate(()=>window.__T.foe()); await p.waitForTimeout(330); await p.screenshot({ path: `t_${tag}_claw.png` }); await p.waitForTimeout(1200); }
    for (const k of ['vic','lvl','shop','trade','sold']) { await p.evaluate(k=>window.__T[k](), k); await p.waitForTimeout(k==='lvl'?1900:k==='trade'?3200:700); await p.screenshot({ path: `t_${tag}_${k}.png` }); }
    console.log(tag, errs.join(' | ')||'no errors');
  } await b.close(); })();
