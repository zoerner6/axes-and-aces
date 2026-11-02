/* Drive the dice tray and check it behaves: which dice light up, what is
   tappable, what the wind-up reads, and how big a die comes out at 320 wide.
     node dev/gen/fktray.cjs */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json','.jpg':'image/jpeg'};
execFileSync('python', ['dev/gen/harness.py','dev/farkle.html','farkletest.html'], {stdio:'inherit'});
const srv = http.createServer((q,r)=>{
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/,'') || 'farkletest.html';
  const f = path.join(ROOT, rel);
  if(!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){ r.writeHead(404); return r.end('no'); }
  r.writeHead(200, {'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream'});
  fs.createReadStream(f).pipe(r);
});
const q = (p, js) => p.evaluate(x => window.__A.ev(x), js);
(async () => {
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/farkletest.html`;
  const b = await chromium.launch();
  for(const [w,h] of [[390,844],[375,667],[360,740],[320,568]]){
    const c2 = await b.newContext({viewport:{width:w,height:h}, deviceScaleFactor:2, isMobile:true, hasTouch:true, reducedMotion:'reduce'});
    const q2 = await c2.newPage();
    await q2.goto(base, {waitUntil:'load'}); await q2.waitForTimeout(300);
    await q2.evaluate(x => window.__A.ev(x), 'started=true; rolling=false;');
    await q2.evaluate(()=>window.__FK.setFaces([1,1,5,5,2,3]));
    await q2.click('[data-die="0"]'); await q2.waitForTimeout(120);
    const r = await q2.evaluate(()=>{
      const live=[...document.getElementById('liveRow').querySelectorAll('.die')];
      const held=[...document.getElementById('heldRow').querySelectorAll('.die')];
      const d=(live[0]||held[0]).getBoundingClientRect();
      const pip=document.querySelector('.die i').getBoundingClientRect();
      const hd=held[0]?held[0].getBoundingClientRect():null;
      const sameCol = hd ? Math.round(hd.left - live.concat(held).filter(e=>+e.dataset.die===0)[0].getBoundingClientRect().left) : 0;
      const col0Live = live.find(e=>+e.dataset.die===1);
      return { die:Math.round(d.width), pip:+pip.width.toFixed(1),
               heldLeft: hd?Math.round(hd.left):null,
               liveLeftOfNext: col0Live?Math.round(col0Live.getBoundingClientRect().left):null,
               side: document.documentElement.scrollWidth - document.documentElement.clientWidth };
    });
    console.log(`  ${w}x${h}  die ${r.die}px  pip ${r.pip}px  ${r.die>=44?'OK':'UNDER 44'}  sideScroll ${r.side}`);
    await c2.close();
  }
  const ctx = await b.newContext({viewport:{width:320,height:568}, deviceScaleFactor:2,
    isMobile:true, hasTouch:true, reducedMotion:'reduce'});
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('console', m => { if(m.type()==='error') errs.push(m.text()); });
  await p.goto(base, {waitUntil:'load'});
  await p.waitForTimeout(400);

  console.log('phone CSS live:', await p.evaluate(()=>matchMedia('(max-width:560px)').matches));
  console.log('die box at 320 wide:', await p.evaluate(()=>{
    const d = document.querySelector('.die').getBoundingClientRect();
    const pip = document.querySelector('.die i').getBoundingClientRect();
    return `die ${Math.round(d.width)}x${Math.round(d.height)}  pip ${Math.round(pip.width)}px`;
  }));
  console.log('all blank before the first roll:',
    await p.evaluate(()=>[...document.querySelectorAll('.die')].every(e=>e.classList.contains('blank'))));

  await q(p, 'started=true; rolling=false;');
  await p.evaluate(()=>window.__FK.setFaces([2,2,2,1,5,4]));
  await p.waitForTimeout(120);
  console.log('\nroll 2-2-2-1-5-4:');
  for(const x of await p.evaluate(()=>[...document.querySelectorAll('.die')].map((e,i)=>
      `  die ${i} = ${e.getAttribute('aria-label').replace('Die showing ','')}  ${e.classList.contains('can')?'LIT':'dead'}  ${e.disabled?'(not tappable)':'(tappable)'}`)))
    console.log(x);

  await p.click('[data-die="0"]'); await p.waitForTimeout(100);
  console.log('\ntap one 2  -> wind', await p.evaluate(()=>document.getElementById('windNum').textContent),
    '| Roll', await p.evaluate(()=>document.getElementById('rollBtn').disabled?'disabled':'ENABLED'),
    '| Strike', await p.evaluate(()=>document.getElementById('strikeBtn').disabled?'disabled':'ENABLED'));
  await p.click('[data-die="1"]'); await p.click('[data-die="2"]'); await p.waitForTimeout(140);
  console.log('tap all three  -> wind', await p.evaluate(()=>document.getElementById('windNum').textContent),
    '| Roll', await p.evaluate(()=>document.getElementById('rollBtn').disabled?'disabled':'ENABLED'),
    '|', await p.evaluate(()=>document.getElementById('strikeNote').textContent),
    '|', await p.evaluate(()=>document.getElementById('rollNote').textContent));
  console.log('held row holds', await p.evaluate(()=>document.getElementById('heldRow').querySelectorAll('.die').length), 'dice');
  console.log('the lone 4 tappable?', await p.evaluate(()=>!document.querySelector('[data-die="5"]').disabled));

  /* a farkle */
  await q(p, 'newTurn(); started=true;');
  await p.evaluate(()=>window.__FK.setFaces([2,3,4,6,2,3]));
  await p.waitForTimeout(120);
  console.log('\nroll 2-3-4-6-2-3 (a farkle): any die tappable?',
    await p.evaluate(()=>[...document.querySelectorAll('.die')].some(e=>!e.disabled)),
    '| isFarkle says', await p.evaluate(()=>window.__FK.isFarkle(window.__FK.facesOf(window.__FK.rollIdx()))));

  /* the straight */
  await q(p, 'newTurn(); started=true;');
  await p.evaluate(()=>window.__FK.setFaces([1,2,3,4,5,6]));
  await p.waitForTimeout(120);
  for(let i=0;i<6;i++) await p.click(`[data-die="${i}"]`);
  await p.waitForTimeout(140);
  console.log('straight, all six set aside -> wind', await p.evaluate(()=>document.getElementById('windNum').textContent),
    '|', await p.evaluate(()=>document.getElementById('rollNote').textContent));

  fs.mkdirSync('dev/gen/out/fk', {recursive:true});
  /* a mixed tray: some set aside, some still live - the normal look */
  await q(p, 'newTurn(); started=true;');
  await p.evaluate(()=>window.__FK.setFaces([1,5,3,3,6,2]));
  await p.click('[data-die="0"]'); await p.click('[data-die="1"]');
  await p.waitForTimeout(160);
  await p.screenshot({path:'dev/gen/out/fk/tray_320.png'});
  console.log('top bar rows:', await p.evaluate(()=>{
    const t=document.querySelector('.top').getBoundingClientRect();
    return Math.round(t.height)+'px tall';
  }));
  console.log('\njs errors:', errs.length ? errs : 'none');
  await b.close(); srv.close();
})();
