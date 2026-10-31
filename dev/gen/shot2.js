const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [w,h,tag] of [[1100,900,'desk'],[400,820,'phone']]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    const errs=[]; p.on('pageerror', e=>errs.push(e.message));
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(800);
    for (let i=0;i<3;i++){ await p.click('[data-act=storyNext]'); await p.waitForTimeout(300); }
    await p.click('[data-act=fight]'); await p.waitForTimeout(600);
    await p.click('.skip').catch(()=>{}); await p.waitForTimeout(1200);
    await p.screenshot({ path: `s_${tag}_fight.png` });
    if(tag==='desk'){ await p.click('[data-act=soldier]'); await p.waitForTimeout(500); await p.screenshot({ path: `s_${tag}_soldier.png` }); }
    console.log(tag, errs.join(' | ') || 'no errors');
  }
  await b.close();
})();
