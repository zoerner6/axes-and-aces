/* What a game of Klondike is actually worth, and how much room it needs.

   node dev/gen/klondike.cjs [--games 20000]

   Monster Solitaire is Klondike now - the one people mean when they say
   solitaire. Before any of it can be built, two things have to be measured
   rather than guessed, and both decide things that are expensive to change
   later:

   1. HOW DEEP A COLUMN GETS. Seven columns fit a 320px phone at 41.7px a
      card, which is the width the Tri-Peaks board proved readable. Across is
      fine. Down is the question: a column stacks, and if the worst case is
      twenty cards deep the board cannot be shown on a phone at all. This
      reports the real distribution rather than the theoretical worst case.

   2. WHAT A GAME DELIVERS. The monster's health is built on it, the way
      ROUND_AVG = 839 was built on dev/gen/peakdeal.cjs. A card going up to a
      foundation is what hits, and sending several without touching the stock
      multiplies, so what matters is both the total and the shape.

   Rules: standard Klondike. Seven columns, one more card each, top card face
   up. Four foundations, ace up to king by suit. Tableau builds down in
   alternating colours. A king goes to an empty column. Draw one from the
   stock, unlimited passes - draw three is about one game in three winnable
   and that is a bad gift when a game is a monster fight. */

const args = process.argv.slice(2);
const flag = (n, d) => { const i = args.indexOf(n); return i >= 0 ? +args[i + 1] : d; };
const GAMES = flag('--games', 20000);
/* A run lands by itself once it reaches this many cards. Without it the
   endgame is one unbroken run of thirty-odd cards, and runVal * run grows
   quadratically, so a won game deals twenty times what a lost one does:
   1846 average against an 80 median. No monster health survives that spread.
   See the note in dev/solitaire.html above ROUND_AVG. */
const CAP = flag('--cap', 0);

const RED = s => s === 1 || s === 2;              /* 0 spades 1 hearts 2 diamonds 3 clubs */

function deal(rnd = Math.random){
  const d = [];
  for(let s = 0; s < 4; s++) for(let r = 1; r <= 13; r++) d.push({ r, s });
  for(let i = d.length - 1; i > 0; i--){
    const j = (rnd() * (i + 1)) | 0;
    [d[i], d[j]] = [d[j], d[i]];
  }
  const cols = [];
  let k = 0;
  for(let c = 0; c < 7; c++){
    const col = { down: [], up: [] };
    for(let n = 0; n <= c; n++) (n === c ? col.up : col.down).push(d[k++]);
    cols.push(col);
  }
  return { cols, stock: d.slice(k), waste: [], found: [0, 0, 0, 0], pass: 0 };
}

const canFound = (g, c) => g.found[c.s] === c.r - 1;
const canStack = (c, onto) => onto && onto.r === c.r + 1 && RED(c.s) !== RED(onto.s);
const colTop = col => col.up[col.up.length - 1];

/* every move worth considering, cheapest first */
function moves(g){
  const out = [];
  const w = g.waste[g.waste.length - 1];
  /* to a foundation: from the waste, or the top of any column */
  if(w && canFound(g, w)) out.push({ k:'wf' });
  g.cols.forEach((col, i) => {
    const t = colTop(col);
    if(t && canFound(g, t)) out.push({ k:'cf', i });
  });
  /* waste onto a column */
  if(w) g.cols.forEach((col, i) => {
    if(col.up.length ? canStack(w, colTop(col)) : (w.r === 13 && !col.down.length)) out.push({ k:'wc', i });
  });
  /* a run of face-up cards from one column to another */
  g.cols.forEach((col, i) => {
    for(let n = 0; n < col.up.length; n++){
      const head = col.up[n];
      /* only move the whole face-up run from head down, as a player would */
      const movingWholeCol = n === 0 && !col.down.length;
      g.cols.forEach((dst, j) => {
        if(i === j) return;
        if(dst.up.length ? canStack(head, colTop(dst)) : (head.r === 13 && !dst.down.length && !movingWholeCol)) {
          out.push({ k:'cc', i, j, n });
        }
      });
    }
  });
  return out;
}

function apply(g, m){
  if(m.k === 'wf'){ const c = g.waste.pop(); g.found[c.s] = c.r; return c; }
  if(m.k === 'cf'){ const c = g.cols[m.i].up.pop(); g.found[c.s] = c.r; flip(g.cols[m.i]); return c; }
  if(m.k === 'wc'){ g.cols[m.i].up.push(g.waste.pop()); return null; }
  if(m.k === 'cc'){
    const run = g.cols[m.i].up.splice(m.n);
    g.cols[m.j].up.push(...run);
    flip(g.cols[m.i]);
    return null;
  }
}
const flip = col => { if(!col.up.length && col.down.length) col.up.push(col.down.pop()); };

function draw(g){
  if(!g.stock.length){
    if(!g.waste.length) return false;
    g.stock = g.waste.reverse(); g.waste = []; g.pass++;
    return g.pass <= 3;                       /* three times round and no more */
  }
  g.waste.push(g.stock.pop());
  return true;
}

/* A deliberately ordinary player. The first version of this looped forever -
   it would move a run from one column to another and then back, two thousand
   times, winning nothing. The rule that kills that is the one a person
   follows without thinking: NEVER make a tableau move that does not reveal a
   face-down card, empty a column, or come off the waste. A shuffle that
   changes nothing is not a move.

   Not clever beyond that, on purpose. Building the damage on perfect play
   would make every fight too hard for everyone who is not a solver. */
function play(g, cap = 400){
  let sent = 0, chain = 0, chainVal = 0, best = 0, draws = 0, steps = 0;
  const chains = [];
  let sinceProgress = 0;
  const depth = () => Math.max(...g.cols.map(c => c.down.length + c.up.length));
  let deepest = depth(), deepestUp = Math.max(...g.cols.map(c => c.up.length));

  const note = () => {
    deepest = Math.max(deepest, depth());
    deepestUp = Math.max(deepestUp, Math.max(...g.cols.map(c => c.up.length)));
  };
  const breakChain = () => { if(chain){ chains.push([chain, chainVal]); if(chain > best) best = chain; } chain = 0; chainVal = 0; };

  while(steps++ < cap){
    const ms = moves(g);

    /* 1. anything that can go up, goes up */
    const up = ms.filter(m => m.k === 'wf' || m.k === 'cf');
    if(up.length){
      const c = apply(g, up[0]);
      sent++; chain++; chainVal += Math.min(c.r, 10);
      if(CAP && chain >= CAP) breakChain();
      sinceProgress = 0; note();
      if(g.found.every(f => f === 13)) break;
      continue;
    }

    /* 2. a move that turns a face-down card over */
    const reveals = ms.filter(m => m.k === 'cc' && m.n === 0 && g.cols[m.i].down.length > 0);
    /* 3. or that empties a column outright */
    const empties = ms.filter(m => m.k === 'cc' && m.n === 0 && !g.cols[m.i].down.length);
    /* 4. or puts the waste card to work */
    const fromWaste = ms.filter(m => m.k === 'wc');

    const pick = reveals[0] || fromWaste[0] || empties[0];
    if(pick){
      breakChain();
      apply(g, pick);
      sinceProgress = 0; note();
      continue;
    }

    /* 5. nothing useful: turn a card */
    breakChain();
    if(!draw(g)) break;
    draws++;
    /* a whole pass of the stock with nothing to show for it means the game
       is over whatever the rules say */
    if(++sinceProgress > g.stock.length + g.waste.length + 2) break;
  }
  breakChain();
  const won = g.found.every(f => f === 13);
  return { won, sent, chains, best, draws, steps, deepest, faceUpDeepest: deepestUp,
           suits: g.found.filter(f => f === 13).length };
}

/* ---- run it ---- */
const avg = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;
const pct = (a, b) => (100 * a / b).toFixed(1) + '%';

let wins = 0;
const sents = [], deeps = [], ups = [], bests = [], stepsArr = [], dmg = [];
/* the four numbers the fight is built on, measured the same way
   dev/gen/peakdeal.cjs measures them for the other board */
const blows = [], breaks = [], suitsHome = [];
const upHist = new Array(30).fill(0);

for(let n = 0; n < GAMES; n++){
  const g = deal();
  const r = play(g);
  if(r.won) wins++;
  sents.push(r.sent); deeps.push(r.deepest); ups.push(r.faceUpDeepest);
  bests.push(r.best); stepsArr.push(r.steps);
  upHist[Math.min(29, r.faceUpDeepest)]++;
  /* the blow a chain lands is its length times the cards in it, the same
     shape Tri-Peaks uses, so the two games can share one fight */
  dmg.push(r.chains.reduce((a, [len, val]) => a + val * len, 0));
  r.chains.forEach(([len, val]) => blows.push(val * len));
  breaks.push(r.chains.length);
  suitsHome.push(r.suits);
}
sents.sort((a, b) => a - b); dmg.sort((a, b) => a - b); ups.sort((a, b) => a - b);
const p = (arr, q) => arr[Math.floor(arr.length * q)];

console.log(`Klondike, draw one, three passes. ${GAMES} games by an ordinary player.\n`);
console.log(`  games won                   : ${pct(wins, GAMES)}`);
console.log(`  cards sent up, avg/med      : ${avg(sents).toFixed(1)} / ${p(sents, .5)} of 52`);
console.log(`  longest chain, avg/90th     : ${avg(bests).toFixed(2)} / ${p(bests.slice().sort((a,b)=>a-b), .9)}`);
console.log(`  GAME DAMAGE  avg/med/90th   : ${avg(dmg).toFixed(0)} / ${p(dmg, .5)} / ${p(dmg, .9)}`);
console.log(`  moves in a game             : ${avg(stepsArr).toFixed(0)}`);
console.log();
console.log(`  THE LAYOUT QUESTION`);
console.log(`  deepest column, any kind    : ${avg(deeps).toFixed(1)} avg, ${Math.max(...deeps)} worst`);
console.log(`  deepest FACE-UP run         : ${avg(ups).toFixed(1)} avg, ${p(ups, .9)} at the 90th, ${Math.max(...ups)} worst`);
console.log(`  face-up depth spread        : ` +
  upHist.map((c, i) => [i, c]).filter(([, c]) => c / GAMES > .004)
    .map(([i, c]) => `${i}:${(100 * c / GAMES).toFixed(0)}%`).join('  '));
console.log();
console.log(`  THE CONSTANTS TO PASTE IN`);
blows.sort((a, b) => a - b);
console.log(`  const ROUND_AVG = ${avg(dmg).toFixed(0)};   /* ${p(dmg, .5)} median */`);
console.log(`  const ROUND_MED = ${p(dmg, .5)};`);
console.log(`  const STRIKES = ${avg(breaks).toFixed(2)};     /* run-breaks in a game */`);
console.log(`  const BLOW_AVG = ${avg(blows).toFixed(0)}, BLOW_MED = ${p(blows, .5)}, BLOW_P90 = ${p(blows, .9)};`);
console.log(`  const SUITS_HOME_AVG = ${avg(suitsHome).toFixed(2)};  /* of four */`);
console.log(`  const CLEAR_RATE = ${(wins / GAMES).toFixed(2)};`);
