const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 800 } });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(600);
  await p.evaluate(()=>window.__T.shop()); await p.waitForTimeout(700); await p.screenshot({ path: 't_shopd.png' }); await b.close(); })();
