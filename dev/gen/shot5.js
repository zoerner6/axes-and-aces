const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 800 } });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(800);
  await p.evaluate(()=>window.__T.shop()); await p.waitForTimeout(800);
  await p.screenshot({ path: 't_shop.png' }); await b.close(); })();
