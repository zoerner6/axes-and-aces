const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[]; const p = await b.newPage({ viewport: { width: 390, height: 840 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(500);
  console.log('start  ', await p.evaluate(()=>window.__T.st()));
  await p.evaluate(()=>window.__T.end1()); await p.waitForTimeout(1500); await p.screenshot({path:'w_knight.png'});
  await p.evaluate(()=>window.__T.next()); await p.waitForTimeout(800);
  console.log('world2 ', await p.evaluate(()=>window.__T.st())); await p.screenshot({path:'w_w2.png'});
  await p.evaluate(()=>window.__T.next()); await p.waitForTimeout(400); await p.evaluate(()=>window.__T.next()); await p.waitForTimeout(800);
  console.log('intro  ', await p.evaluate(()=>window.__T.gen())); await p.screenshot({path:'w_w2fight.png'});
  console.log('w2boss ', await p.evaluate(()=>window.__T.boss()));
  for (const w of [5,9,10,11,25]) { await p.evaluate(w=>window.__T.jump(w),w); await p.waitForTimeout(300); console.log('w'+w, await p.evaluate(()=>window.__T.st()), await p.evaluate(()=>window.__T.boss())); }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
