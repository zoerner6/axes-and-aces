/* Does every perk and charm actually do something on the Klondike board?
     node dev/gen/klgear.cjs

   dev/gen/slperks.cjs and dev/gen/slcharms.cjs ask this of Tri-Peaks by
   poking R.tableau, which does not exist here, so this asks it of the board
   the game now opens on. It was worth writing: before it, three of them did
   nothing at all on Klondike and one of them lied.

     Deep Deck      added no cards, because 52 is exactly 28 dealt and 24 in
                    the stock and there was nothing spare to give
     Second Sight   read R.stock[R.si], and Klondike pops off the far end, so
                    it showed the card at the BOTTOM of the deck
     Reader's Glass checked R.hidden, which Klondike has not got
     Marked Deck    and Reader's Glass were the same effect twice

   Each case below sets the hero up, deals, and compares against a hero with
   nothing. A perk that reads NO CHANGE is a perk a player would pay for and
   not receive. */
const { chromium } = require('playwright');
const path = require('path');
process.chdir(path.join(__dirname, '..', '..'));
const URL = 'file:///' + path.resolve('solitaire.html').replace(/\\/g, '/');

const SEED = 20260211;          /* the same deal every time, so a difference is the charm */

(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).slice(0, 140)));
  await p.route('**/*.{mp3,m4a,mp4,webm}', r => r.abort());
  await p.goto(URL, { waitUntil: 'load' });
  await p.waitForTimeout(2000);

  /* a fixed shuffle, so two deals differ only by what the hero is carrying */
  const look = (perks, charms) => p.evaluate(({ perks, charms, seed }) => {
    const X = window.__SOL;
    X.S.perks = perks; X.S.charms = charms; X.S.board = 'klondike';
    let n = seed;
    const rnd = () => ((n = (n * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
    X.R = X.dealRound({ rnd });
    /* openBoard, not render: Iron Cup is put up when a board OPENS, and a
       test that only renders would report a charm the game does apply as
       doing nothing. Same for maxHp, which is set when a hero levels. */
    X.S.block = 0;
    /* heroMaxHP is the level curve alone; Tough as Nails adds to bonusHp when
       it is TAKEN, so a test that only sets S.perks has to add it too, or it
       reports a working perk as doing nothing. */
    X.S.bonusHp = 40 * X.perkCount('tough');
    X.S.maxHp = X.heroMaxHP(X.S.level) + X.S.bonusHp;
    X.openBoard();
    const R = X.R;
    const back = document.querySelector('[data-act="draw"]');
    return {
      stock: R.stock.length,
      down: R.cols.reduce((a, c) => a + c.down.length, 0),
      up: R.cols.reduce((a, c) => a + c.up.length, 0),
      cards: R.cols.reduce((a, c) => a + c.down.length + c.up.length, 0),
      cap: R.cap, wild: !!R.wild, coin: !!R.coin, guard: X.S.block | 0,
      maxHp: X.S.maxHp,
      peek: back ? (back.textContent || '').trim() : '',
      /* and whether that peek is the truth */
      peekRight: !!back && (back.textContent || '').trim() !== '' &&
        (() => { const c = R.stock[R.stock.length - 1];
          return (back.textContent || '').includes(X.RANKS ? X.RANKS[c.r] : ''); })(),
      nextCard: (() => { const c = R.stock[R.stock.length - 1]; return c ? `${c.r}/${c.s}` : ''; })(),
    };
  }, { perks, charms, seed: SEED });

  const base = await look([], []);
  console.log('a hero carrying nothing:');
  console.log(`  ${base.cards} cards dealt (${base.up} up, ${base.down} down), ${base.stock} in the stock, ` +
    `run cap ${base.cap}, guard ${base.guard}, health ${base.maxHp}\n`);

  const cases = [
    ['Deep Deck',        ['deep'], [],          r => r.stock !== base.stock,  r => `stock ${base.stock} -> ${r.stock}`],
    ['Deep Deck x2',     ['deep', 'deep'], [],  r => r.stock > base.stock + 3, r => `stock ${base.stock} -> ${r.stock}`],
    ['Second Sight',     ['sight'], [],         r => r.peek !== '' && r.peekRight,
                                                 r => `the deck back reads "${r.peek}" and the next card is ${r.nextCard}`],
    ['Wild Ace',         ['wild'], [],          r => r.wild !== base.wild,    r => `wild ${base.wild} -> ${r.wild}`],
    ['Tough as Nails',   ['tough'], [],         r => r.maxHp !== base.maxHp,  r => `health ${base.maxHp} -> ${r.maxHp}`],
    ['Long Memory',      ['long'], [],          () => 'blow',                 () => 'changes the blow, not the deal - see klbalance'],
    ['Training',         ['study'], [],         () => 'xp',                   () => 'changes experience, not the deal'],
    ['Marked Deck',      [], ['marked'],        r => r.cards !== base.cards,  r => `cards dealt ${base.cards} -> ${r.cards}`],
    ["Reader's Glass",   [], ['glass'],         r => r.up !== base.up && r.cards === base.cards,
                                                 r => `face up ${base.up} -> ${r.up}, cards dealt ${base.cards} -> ${r.cards}`],
    ['both, and different', [], ['marked', 'glass'],
                                                r => r.cards < base.cards && r.up > base.up,
                                                 r => `cards ${base.cards} -> ${r.cards}, face up ${base.up} -> ${r.up}`],
    ["Jester's Coin",    [], ['jester'],        r => r.coin !== base.coin,    r => `coin ${base.coin} -> ${r.coin}`],
    ['Iron Cup',         [], ['cup'],           r => r.guard !== base.guard,  r => `guard ${base.guard} -> ${r.guard}`],
    ["Gambler's Ring",   [], ['ring'],          () => 'blow',                 () => 'changes the blow, not the deal - see klbalance'],
  ];

  let dead = 0;
  for(const [name, perks, charms, test, say] of cases){
    const r = await look(perks, charms);
    const ok = test(r);
    if(ok === false) dead++;
    console.log(`  ${name.padEnd(22)} ${ok === false ? '*** NO CHANGE ***  ' : ok === true ? 'changes the deal   ' : 'not a deal change  '}${say(r)}`);
  }

  /* and the words, which are the other half of a charm working */
  console.log('\nwhat the shop says, on each board:');
  for(const board of ['klondike', 'peaks']){
    const said = await p.evaluate(bk => {
      window.__SOL.S.board = bk;
      return window.__SOL.CHARMS.map(c => `${c.name}: ${window.__SOL.charmDesc(c)}`);
    }, board);
    console.log(`  ${board}`);
    said.forEach(l => console.log(`    ${l}`));
  }

  console.log(dead ? `\n${dead} do nothing on this board` : '\nevery perk and charm changes something');
  console.log(errs.length ? 'ERRORS: ' + [...new Set(errs)].join(' | ') : 'no page errors');
  await b.close();
  process.exit(dead ? 1 : 0);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
