const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
  for (const [w,h] of [[390,820],[1100,800]]) { const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(500);
    for (const k of ['vic','shop','sold']) { await p.evaluate(k=>window.__T[k](),k); await p.waitForTimeout(k==='vic'?2600:600); await p.screenshot({ path: `x_${w}_${k}.png` }); } }
  await b.close(); })();
