const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [w,h,tag] of [[1100,900,'desk'],[400,820,'phone']]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    const errs=[]; p.on('pageerror', e=>errs.push(e.message)); p.on('console', m=>{ if(m.type()==='error') errs.push(m.text()); });
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(1200);
    await p.screenshot({ path: `s_${tag}_story.png` });
    for (let i=0;i<3;i++){ await p.click('[data-act=storyNext]'); await p.waitForTimeout(400); }
    await p.screenshot({ path: `s_${tag}_intro.png` });
    await p.click('[data-act=fight]'); await p.waitForTimeout(800);
    await p.click('.skip').catch(()=>{}); await p.waitForTimeout(800);
    await p.screenshot({ path: `s_${tag}_fight.png` });
    console.log(tag, errs.join(' | ') || 'no errors');
  }
  await b.close();
})();
