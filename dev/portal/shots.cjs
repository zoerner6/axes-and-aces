/* The three gameplay screenshots Poki asks for on the submission form.

   Taken from the Poki package itself, so what a reviewer sees in the picture is
   what they get in the build: the still monster art, no leaderboard buttons, no
   share buttons. 16:9, which is the canvas shape Poki require.

     node dev/portal/shots.cjs [--url http://127.0.0.1:8842/audittest.html]
                               [--out store/portal]
*/
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const args = process.argv.slice(2);
const flag = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const URL = flag('--url', 'http://127.0.0.1:8842/audittest.html');
const OUT = flag('--out', 'store/portal');

const KIT = `localStorage.clear();
  S.idx=8; S.level=7; S.maxHp=900; S.hp=760; S.gold=24;
  S.eq={main:{type:'axe',tier:4},off:null,shield:{type:'shield',tier:3},
        helm:{type:'helm',tier:3},armor:{type:'armor',tier:4}};
  S.spells=['potion','ironskin','rage']; S.coach=-1;
  S.tips={shop:1,level:1,boss:1,path:1};`;

const SHOTS = [
  ['screenshot-1-fight', `${KIT} S.foePick='troll'; S.enc='spot'; fightIntro();`, 'fight',
   `S.fight.hand=[cid(14,0),cid(14,1),cid(14,2),cid(13,0),cid(13,1),cid(10,1),cid(3,2)];
    sel=[]; render(); document.getElementById('hintBtn').click();`],
  /* The dragon, not the Cellar Ghoul. The ghoul is still in the game and
     a reviewer will meet it; it is simply not what the pitch leads with. */
  ['screenshot-2-boss', `${KIT} S.idx=11; S.foePick='dragon'; S.enc='boss'; fightIntro();`, null, null],
  ['screenshot-3-reward', `${KIT} S.gold=60; S.shopTab='smith'; shopPanel();`, null, null],
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  for (const [name, setup, extra, after] of SHOTS) {
    const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
    const p = await ctx.newPage();
    await p.goto(URL, { waitUntil: 'load' });
    await p.waitForTimeout(1400);
    await p.evaluate(x => window.__A.ev(x), setup);
    await p.waitForTimeout(4200);
    if (extra === 'fight') {
      const btn = await p.$('[data-act=fight]');
      if (btn) { await btn.click({ force: true }); await p.waitForTimeout(2600); }
    }
    if (after) { await p.evaluate(x => window.__A.ev(x), after); await p.waitForTimeout(1600); }
    const file = path.join(OUT, `${name}.png`);
    await p.screenshot({ path: file });
    console.log(`  ${name}.png  1920x1080  ${(fs.statSync(file).size / 2 ** 20).toFixed(1)} MB`);
    await ctx.close();
  }
  await b.close();
})().catch(e => { console.error('SHOTS FAILED:', e.message); process.exit(1); });
