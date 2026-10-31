const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 800 } });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(800);
  await p.evaluate(()=>window.__T.shop()); await p.waitForTimeout(700); await p.screenshot({ path: 't_shop3.png' });
  await p.click('[data-act=close]').catch(()=>{}); await p.evaluate(()=>{document.getElementById('overlay').hidden=true}); await p.waitForTimeout(300);
  await p.screenshot({ path: 't_tmp.png' }); await b.close(); })();
