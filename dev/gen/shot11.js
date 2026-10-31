const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 820 } });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(600);
  await p.evaluate(()=>window.__T.vic()); await p.waitForTimeout(2600); await p.screenshot({ path: 't_vic.png' }); await b.close(); })();
