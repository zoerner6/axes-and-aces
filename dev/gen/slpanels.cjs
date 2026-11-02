/* Does every popup fit, with its main button reachable without scrolling?

   node dev/gen/slpanels.cjs [--shot out.png]

   Josh's rule, from dev/plans/solitaire.md: no popup ever needs scrolling to
   reach its main button. That is not a nicety at 320x568, where an intro has
   to hold a picture, a line of talk, a six-number tape, a boss rule and a
   Fight button inside 540 usable pixels. This opens each one and measures it.

   It also checks the ordinary things a person would notice: text on text,
   art sliced by its frame, words cut off, tap targets under 44px. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const args = process.argv.slice(2);
const shotAt = args.includes('--shot') ? args[args.indexOf('--shot') + 1] : null;

execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
const built = fs.readFileSync(path.join(ROOT, 'solitaire.html'), 'utf8');
const audit = fs.readFileSync(path.join(ROOT, 'dev/gen/audit.js'), 'utf8');
const out = path.join(ROOT, 'soltest.html');
fs.writeFileSync(out, built + `\n<script>${audit}</script>\n`);

const SIZES = [[320, 568], [360, 740], [375, 667], [390, 844], [1280, 800]];
const PLAIN = s => String(s).replace(/\s+/g, ' ').trim();

(async () => {
  const b = await chromium.launch();
  let bad = 0;

  for (const [w, h] of SIZES) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2,
      isMobile: w <= 560, hasTouch: w <= 560 });
    const p = await ctx.newPage();
    await p.route('**/vid/**', r => r.abort());
    const errs = [];
    p.on('pageerror', e => errs.push(PLAIN(e.message).slice(0, 150)));
    await p.goto('file://' + out.replace(/\\/g, '/'), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);

    /* The four intros, then the screens a fight ends on. The level-up has no
       one big button - its main control is the list of perks - so what has to
       be reachable there is the LAST perk, not a button. */
    const SCREENS = ['ambush', 'spot', 'path', 'boss', 'victory', 'flawless', 'clean', 'level', 'fallen',
                     'rest', 'smith', 'charms', 'pots'];
    for (const kind of SCREENS) {
      await p.evaluate(k => {
        const SOL = window.__SOL, S = SOL.S;
        S.step = k === 'boss' ? 2 : 0;
        S.area = 0;
        S.perks = []; S.bonusHp = 0; S.pendingLv = 0;
        S.level = k === 'level' ? 4 : 1;
        S.maxHp = 400 + 100 * (S.level - 1); S.hp = Math.round(S.maxHp * .4);
        S.gold = 37; S.xp = 0;
        SOL.startFight();
        SOL.closePanel();
        if (['ambush', 'spot', 'path', 'boss'].includes(k)) return SOL.fightIntro(k);
        if (k === 'level') { S.pendingLv = 1; return SOL.levelPanel(); }
        if (k === 'fallen') return SOL.lost();
        if (['rest', 'smith', 'charms', 'pots'].includes(k)) {
          /* a player who has been shopping: some gold, a charm, a potion, and
             mid-tier gear, which is when the rows are at their tallest */
          S.gold = 64; S.level = 6;
          S.maxHp = 400 + 100 * 5; S.hp = Math.round(S.maxHp * .55);
          S.charms = ['cup']; S.pots = ['heal'];
          S.eq = { main: { type: 'sword', tier: 2 }, armor: { type: 'armor', tier: 1 } };
          return SOL.shopPanel(k);
        }
        const d = S.fight;
        const mood = { flawless: k === 'flawless', clean: k === 'clean', clutch: false };
        mood.bonus = mood.flawless ? d.gold : 0;
        S.gold += d.gold + mood.bonus;
        S.xp += d.xp;
        SOL.victoryPanel(d, mood);
      }, kind);
      await p.waitForTimeout(kind === 'fallen' ? 2400 : 1700);   /* typed lines, counters */

      const m = await p.evaluate(() => {
        const PLAIN = s => String(s).replace(/\s+/g, ' ').trim();   /* the page needs its own */
        const panel = document.querySelector('#panel');
        /* the main control: one big button, or the last perk on a level-up */
        const perks = [...panel.querySelectorAll('.perk')];
        const btn = panel.querySelector('.btn.big') || perks[perks.length - 1] || null;
        const pr = panel.getBoundingClientRect();
        const br = btn ? btn.getBoundingClientRect() : null;
        return {
          panelH: Math.round(pr.height),
          scrollH: panel.scrollHeight,
          clientH: panel.clientHeight,
          scrolls: panel.scrollHeight > panel.clientHeight + 1,
          btn: br ? { h: Math.round(br.height), bottom: Math.round(br.bottom),
                      inView: br.bottom <= innerHeight + 1 && br.top >= -1 } : null,
          tag: PLAIN((panel.querySelector('.scene .tag') || {}).textContent || ''),
          say: PLAIN((panel.querySelector('#encSay') || {}).textContent || ''),
          cap: PLAIN((panel.querySelector('#encCap') || {}).textContent || ''),
          rule: PLAIN((panel.querySelector('.tipbox') || {}).textContent || ''),
          audit: window.__AUDIT('panel'),
        };
      });

      const a = m.audit, notes = [];
      if (m.scrolls) { notes.push(`panel scrolls: ${m.scrollH}px of content in ${m.clientH}px`); bad++; }
      if (!m.btn) { notes.push('nothing to press'); bad++; }
      else {
        if (!m.btn.inView) { notes.push(`the main control sits ${m.btn.bottom - h}px below the screen`); bad++; }
        if (m.btn.h < 44) { notes.push(`the main control is only ${m.btn.h}px tall`); bad++; }
      }
      if (kind === 'boss' && !m.rule) { notes.push('boss intro shows no rule'); bad++; }
      if (['ambush', 'spot', 'path', 'boss'].includes(kind) && !m.say) { notes.push('nothing was said'); bad++; }
      if (a.overlaps.length) { notes.push('text on text: ' + a.overlaps.map(o => `"${o.a}" x "${o.b}"`).join(' | ')); bad++; }
      if (a.cropped.length) { notes.push('art sliced: ' + a.cropped.map(c => `${c.src} sides ${c.cutSides} topbottom ${c.cutTopBottom}`).join(' | ')); bad++; }
      if (a.broken.length) { notes.push('missing art: ' + a.broken.join(', ')); bad++; }
      if (a.clipped && a.clipped.length) { notes.push('clipped: ' + a.clipped.map(c => PLAIN(c.text || c)).join(' | ')); bad++; }
      if (a.tiny && a.tiny.length) { notes.push('tiny type: ' + a.tiny.map(t => PLAIN(t.text || t)).join(' | ')); bad++; }

      console.log(`${String(w).padStart(4)}x${h} ${kind.padEnd(7)} panel ${String(m.panelH).padStart(3)}px ` +
        `content ${String(m.scrollH).padStart(3)}  button bottom ${m.btn ? m.btn.bottom : '-'} of ${h}  ` +
        `"${m.tag}" / "${m.say}"`);
      notes.forEach(n => console.log('      ** ' + n));

      if (shotAt && w === 320) await p.screenshot({ path: shotAt.replace('.png', `_${kind}.png`) });
    }
    if (errs.length) { console.log('      ** JS: ' + [...new Set(errs)].join(' | ')); bad++; }
    await ctx.close();
  }
  await b.close();
  console.log(bad ? `\n${bad} problems` : '\nevery popup fits');
  if (bad) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
