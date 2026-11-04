/* Record the preview videos CrazyGames asks for at submission.

   They want a landscape 16:9 and a portrait 2:3 clip, both 1080p, 15 to 20
   seconds, no sound and no fast-forwarding. So this plays the game for real in
   a headless browser and films it: a hero worth looking at walks into a boss,
   plays a full house, then a straight flush, and the troll goes down.

   The hands are dealt on purpose. Left to chance the trailer shows "High Card",
   which is a true picture of the game and a poor advertisement for it.

   It writes the raw recording plus the offset each beat happened at, so
   dev/portal/preview.py can cut the clip without anyone guessing.

     node dev/portal/trailer.cjs [--url http://127.0.0.1:8765/audittest.html]
                                 [--out dev/gen/out/trailer]
*/
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const args = process.argv.slice(2);
const flag = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const URL = flag('--url', 'http://127.0.0.1:8765/audittest.html');
const OUT = flag('--out', 'dev/gen/out/trailer');

/* A hero far enough in to have gear and spells worth looking at. */
const KIT = `localStorage.clear();
  S.idx=8; S.level=7; S.maxHp=900; S.hp=900; S.gold=24;
  S.eq={main:{type:'axe',tier:4},off:null,shield:{type:'shield',tier:3},
        helm:{type:'helm',tier:3},armor:{type:'armor',tier:4}};
  S.spells=['potion','ironskin','rage']; S.coach=-1;
  S.tips={shop:1,level:1,boss:1,path:1};
  S.huntFoe=null; S.foePick='troll'; S.enc='boss'; fightIntro();`;

/* Aces full of kings, then a straight flush in spades. Clubs are the suit the
   Troll King shrugs off, so neither hand wastes itself on him. */
const FULL_HOUSE = `S.fight.hand=[cid(14,0),cid(14,1),cid(14,2),cid(13,0),cid(13,1),cid(10,1),cid(3,2)];
  sel=[]; infoSel=null; render();`;
const STRAIGHT_FLUSH = `S.fight.hand=[cid(9,0),cid(10,0),cid(11,0),cid(12,0),cid(13,0),cid(2,1),cid(4,2)];
  sel=[]; infoSel=null; render();`;

async function film(name, viewport, scale) {
  const dir = path.join(OUT, name);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });

  const b = await chromium.launch();
  const t0 = Date.now();
  const ctx = await b.newContext({
    viewport, deviceScaleFactor: scale,
    isMobile: viewport.width < 600, hasTouch: viewport.width < 600,
    recordVideo: { dir, size: { width: viewport.width * scale, height: viewport.height * scale } },
  });
  const marks = {};
  const at = k => { marks[k] = (Date.now() - t0) / 1000; };

  const p = await ctx.newPage();
  await p.goto(URL, { waitUntil: 'load' });
  await p.waitForTimeout(900);
  await p.evaluate(x => window.__A.ev(x), KIT);
  at('bossIntro');
  await p.waitForTimeout(3800);                  // the boss has its say

  const click = async (sel, wait) => {
    const el = await p.$(sel);
    if (el) await el.click({ force: true }).catch(() => {});
    await p.waitForTimeout(wait);
  };
  const deal = async hand => { await p.evaluate(x => window.__A.ev(x), hand); };

  await click('[data-act=fight]', 1800);
  at('fightStart');
  await deal(FULL_HOUSE);
  await p.waitForTimeout(700);
  await click('#hintBtn', 1100);
  await click('#atkBtn', 4200);
  at('firstHit');

  const done = await p.evaluate(() => !document.getElementById('overlay').hidden);
  if (!done) {
    await deal(STRAIGHT_FLUSH);
    await p.waitForTimeout(700);
    await click('#hintBtn', 1100);
    await click('#atkBtn', 5200);
  }
  at('kill');
  await p.waitForTimeout(3200);                  // the body drops and the loot flies
  at('end');

  await ctx.close();
  await b.close();

  const vids = fs.readdirSync(dir).filter(f => f.endsWith('.webm'))
    .map(f => path.join(dir, f)).filter(f => fs.statSync(f).size > 0);
  if (!vids.length) throw new Error('no video recorded for ' + name);
  const src = vids.sort((a, c) => fs.statSync(c).size - fs.statSync(a).size)[0];
  console.log(`${name}: ${(fs.statSync(src).size / 2 ** 20).toFixed(1)} MB`,
              JSON.stringify(marks));
  return { src, marks, width: viewport.width * scale, height: viewport.height * scale };
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const out = {};
  out.landscape = await film('landscape', { width: 1280, height: 720 }, 1.5);
  out.portrait = await film('portrait', { width: 540, height: 810 }, 2);
  fs.writeFileSync(path.join(OUT, 'sources.json'), JSON.stringify(out, null, 1));
  console.log('wrote', path.join(OUT, 'sources.json'));
})().catch(e => { console.error('TRAILER FAILED:', e.message); process.exit(1); });
