const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
  for (const [w,tag] of [[1340,'d'],[400,'p']]) { const p = await b.newPage({ viewport: { width: w, height: 900 } });
    await p.goto('http://localhost:8765/opts/t.html'); await p.waitForTimeout(1200);
    const sw = await p.evaluate(()=>document.documentElement.scrollWidth); console.log(tag,'scrollWidth',sw);
    await p.screenshot({ path: `o_${tag}.png`, fullPage: true }); }
  await b.close(); })();
