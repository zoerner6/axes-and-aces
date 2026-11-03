/* Does the WORST Klondike board still fit on the smallest phone?
     node dev/gen/kldeep.cjs

   This is the one question Klondike asks that Tri-Peaks never did. A Tri-Peaks
   board is 28 cards in a fixed shape: measure it once at 320x568 and it is
   measured forever. A Klondike column grows. dev/gen/klondike.cjs measured
   11.3 cards deep on average, 18 at the worst, with up to 12 of them face up,
   and no fixed step survives that - at 18px a card the worst column is 364px
   tall and there is no phone that holds that and a monster.

   dev/gen/slscan.cjs scans the board a player is dealt, which is one card per
   column, so it reports the tableau at its SHORTEST and says nothing about any
   of this. The only honest test is to put the worst case on screen and look.

   Three boards, each at every phone size:
     fresh      the opening deal, one card up per column
     average    11 deep, 9 face up
     worst      18 deep, 12 face up, measured as the deepest ever seen */
const { chromium } = require('playwright');
const path = require('path');
process.chdir(path.join(__dirname, '..', '..'));
const URL = 'file:///' + path.resolve('solitaire.html').replace(/\\/g, '/');

const SIZES = [[320, 568], [360, 740], [375, 667], [390, 844], [430, 932], [820, 600]];
const CASES = [
  ['fresh', null],
  ['average', { down: 2, up: 9 }],
  ['worst', { down: 6, up: 12 }],
];

(async () => {
  const b = await chromium.launch();
  let bad = 0;

  for(const [w, h] of SIZES){
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w <= 560, hasTouch: w <= 560 });
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(String(e.message).slice(0, 120)));
    await p.route('**/*.{mp3,m4a,mp4,webm}', r => r.abort());
    await p.goto(URL, { waitUntil: 'load' });
    await p.waitForTimeout
      ? await p.waitForTimeout(1800) : null;
    for(let i = 0; i < 6; i++){
      if(!await p.evaluate(() => { const o = document.getElementById('overlay'); return o && !o.hidden; })) break;
      await p.click('#panel .btn.big[data-act], #panel [data-act]', { timeout: 2500 }).catch(() => {});
      await p.waitForTimeout(700);
    }

    for(const [name, shape] of CASES){
      const m = await p.evaluate(sh => {
        const X = window.__SOL, R = X.R;
        if(sh){
          /* stack the deepest column measured, and leave the others ordinary,
             because a board where every column is deep is not a board that
             happens - the deep one is what has to fit */
          let k = 2;
          const card = () => ({ r: ((k = (k * 7 + 3) % 13) + 1), s: k % 4 });
          R.cols.forEach((col, i) => {
            if(i === 3){
              col.down = Array.from({ length: sh.down }, card);
              col.up = Array.from({ length: sh.up }, card);
            }
          });
        }
        X.render();
        const r = e => e.getBoundingClientRect();
        const cols = document.getElementById('klCols');
        if(!cols) return { missing: true };
        const cards = [...cols.querySelectorAll('.pk')];
        const deepest = [...cols.querySelectorAll('.kl-col')]
          .map(c => c.children.length).sort((a, b) => b - a)[0];
        const col = cols.querySelector('.kl-col[data-col="3"]');
        const kids = col ? [...col.children] : [];
        /* The sliver that matters is the one on a card a thumb has to hit, so
           only face-up cards count. The first version measured every gap,
           including the face-down step - which is 6px on purpose, because a
           face-down card is aria-hidden and tabindex -1 and nobody is ever
           asked to tap one. It reported a 6px target on every board. */
        let sliver = 999;
        for(let i = 0; i + 1 < kids.length; i++){
          if(kids[i].dataset.kind !== 'up') continue;
          sliver = Math.min(sliver, Math.round(r(kids[i + 1]).top - r(kids[i]).top));
        }
        const lastUp = kids.filter(e => e.dataset.kind === 'up').pop();
        const run = document.getElementById('runbox');
        const stage = document.getElementById('stage');
        return {
          deepest,
          colsTop: Math.round(r(cols).top), colsBottom: Math.round(r(cols).bottom),
          colsLeft: Math.round(r(cols).left), colsRight: Math.round(r(cols).right),
          lowestCard: Math.round(Math.max(...cards.map(c => r(c).bottom))),
          runBottom: run ? Math.round(r(run).bottom) : null,
          stageBottom: stage ? Math.round(r(stage).bottom) : null,
          sliver: sliver === 999 ? null : sliver,
          /* the bottom card of a column is never covered, so its whole face
             is the target - worth knowing it is still a real one */
          lastCard: lastUp ? Math.round(r(lastUp).height) : null,
          /* What must not be covered is the monster's PICTURE, not the stage
             box. The stage spans the whole upper area and the board is laid
             over its lower part on purpose, so comparing against the box
             reported an overlap at every size - dev/gen/slscan.cjs, which
             audits the real art, says those sizes are clean. */
          pic: (() => { const i = document.querySelector('#foePic img');
            if(!i) return null; const b = r(i);
            return { top:Math.round(b.top), bottom:Math.round(b.bottom),
                     left:Math.round(b.left), right:Math.round(b.right) }; })(),
          /* The sliver being big enough means nothing if what sits in it is
             bigger. This measures the corner a covered card actually shows:
             the board read as sliced-in-half glyphs while every number here
             said it fitted. */
          rankCut: (() => {
            for(let i = 0; i + 1 < kids.length; i++){
              if(kids[i].dataset.kind !== 'up') continue;
              const cn = kids[i].querySelector('.cn');
              if(!cn) continue;
              const need = Math.ceil(r(cn).bottom - r(kids[i]).top);
              const have = Math.round(r(kids[i + 1]).top - r(kids[i]).top);
              if(need > have + 1) return `needs ${need}px, has ${have}px`;
            }
            return null;
          })(),
          vh: innerHeight,
          scroll: document.documentElement.scrollHeight,
          sideways: document.documentElement.scrollWidth > innerWidth + 1,
        };
      }, shape);

      if(m.missing){ console.log(`${w}x${h}  ${name.padEnd(8)}  NO KLONDIKE BOARD ON SCREEN`); bad++; continue; }
      const notes = [];
      /* the run box is the last thing on the board, so if it is off the bottom
         the player cannot see the number the whole fight is about */
      if(m.runBottom > m.vh) notes.push(`the run box ends ${m.runBottom - m.vh}px below the screen`);
      if(m.scroll > m.vh + 1) notes.push(`the page scrolls ${m.scroll - m.vh}px`);
      if(m.sideways) notes.push('the page scrolls sideways');
      if(m.lowestCard > m.vh) notes.push(`the lowest card is ${m.lowestCard - m.vh}px below the screen`);
      /* a real rectangle intersection. Comparing one edge said the columns
         covered the monster at 820x600, where the board sits BESIDE it. */
      if(m.pic && m.pic.bottom > m.colsTop && m.pic.top < m.colsBottom &&
         m.pic.right > m.colsLeft && m.pic.left < m.colsRight)
        notes.push(`the columns cover the monster by ${m.pic.bottom - m.colsTop}px`);
      if(m.rankCut) notes.push(`a covered card's rank is cut: ${m.rankCut}`);
      /* a covered card is tapped on its sliver, and 8px is about the least a
         thumb can find - klplay proved the sliver is hittable, this proves it
         is still there when the column is deep */
      if(m.sliver != null && m.sliver < 8) notes.push(`a covered card shows only ${m.sliver}px`);
      if(errs.length) notes.push('JS: ' + [...new Set(errs)].join(' | '));
      if(notes.length) bad++;

      console.log(`${String(w).padStart(4)}x${h}  ${name.padEnd(8)}  ` +
        `deepest column ${String(m.deepest).padStart(2)}  ` +
        `board ${String(m.colsBottom - m.colsTop).padStart(3)}px (${m.colsTop}-${m.colsBottom})  ` +
        `face-up sliver ${String(m.sliver == null ? '-' : m.sliver).padStart(3)}px  ` +
        `bottom card ${String(m.lastCard == null ? '-' : m.lastCard).padStart(3)}px  ` +
        `run ends ${String(m.runBottom).padStart(3)} of ${m.vh}`);
      notes.forEach(n => console.log('        ** ' + n));
    }
    await ctx.close();
  }
  console.log(bad ? `\n${bad} boards do not fit` : '\nevery board fits, fresh and at its worst');
  await b.close();
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
