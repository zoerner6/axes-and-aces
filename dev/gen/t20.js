const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  const p = await b.newPage({ viewport: { width: 390, height: 840 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
  for (const [k,t] of [['vic',1500],['sell',3900],['enc',2500],['path',600]]) { await p.evaluate(k=>window.__T[k](),k); await p.waitForTimeout(t); await p.screenshot({ path: `z_${k}.png` });
    console.log(k, await p.evaluate(()=>{const q=document.getElementById('panel');return q.scrollWidth>q.clientWidth+1?'SIDE-SCROLL':'ok'})); }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
