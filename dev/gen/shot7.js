const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 1900 } });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(800);
  await p.evaluate(()=>window.__T.shop()); await p.waitForTimeout(700);
  await p.evaluate(()=>{const q=document.getElementById('panel'); q.style.maxHeight='none';});
  await p.screenshot({ path: 't_shop2.png' }); await b.close(); })();
