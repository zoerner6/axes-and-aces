const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 820 } });
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
  for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
  await p.click('[data-act=fight]'); await p.waitForTimeout(600);
  const r=await p.evaluate(()=>{const e=document.getElementById('discBtn').getBoundingClientRect();return [e.x,e.y,e.width,e.height]});
  await p.screenshot({ path: 'disc.png', clip:{x:r[0]-10,y:r[1]-10,width:r[2]+20,height:r[3]+20} }); await b.close(); })();
