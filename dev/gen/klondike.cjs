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

/* opts.deeper buries the N longest columns one card further down. All seven
   measured at a 39% win rate against an ordinary deal's 84%, which is harsher
   than the hardest rule Tri-Peaks has, so the boss rules take a count. */
function deal(rnd = Math.random, opts = {}){
  const d = [];
  for(let s = 0; s < 4; s++) for(let r = 1; r <= 13; r++) d.push({ r, s });
  for(let i = d.length - 1; i > 0; i--){
    const j = (rnd() * (i + 1)) | 0;
    [d[i], d[j]] = [d[j], d[i]];
  }
  const deep = opts.deeper === true ? 7 : (opts.deeper | 0);
  const cols = [];
  let k = 0;
  for(let c = 0; c < 7; c++){
    const col = { down: [], up: [] };
    const last = c + (c >= 7 - deep ? 1 : 0);
    for(let n = 0; n <= last && k < d.length; n++) (n === last ? col.up : col.down).push(d[k++]);
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

function draw(g, maxPass = 3){
  if(!g.stock.length){
    if(!g.waste.length) return false;
    g.stock = g.waste.reverse(); g.waste = []; g.pass++;
    return g.pass <= maxPass;                 /* three times round, or what a boss allows */
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
function play(g, cap = 400, opts = {}){
  const runCap = opts.runCap != null ? opts.runCap : CAP;
  const maxPass = opts.passes != null ? opts.passes : 3;
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
      if(runCap && chain >= runCap) breakChain();
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
    if(!draw(g, maxPass)) break;
    draws++;
    /* a whole pass of the stock with nothing to show for it means the game
       is over whatever the rules say */
    if(++sinceProgress > g.stock.length + g.waste.length + 2) break;
  }
  breakChain();
  const won = g.found.every(f => f === 13);
  return { won, sent, chains, best, draws, steps, deepest, faceUpDeepest: deepestUp,
           suits: g.found.filter(f => f === 13).length, cleared: won };
}

module.exports = { deal, play, moves, apply, draw, canFound, canStack };
/* required by dev/gen/klbalance.cjs, which wants the board and not the report */
if(require.main !== module) return;

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

/* ---- and the constants FIGHT.klondike is built from ----

   Three things decide these, and all three were forced by what came out of
   the runs above rather than chosen:

   THE RUN CAP. runVal * run grows quadratically and Klondike's endgame is one
   unbroken run of thirty-odd cards, so an uncapped blow made a cleared board
   deal 2215 against a jammed board's 99. No monster health fits a spread of
   twenty-three. Eight is also where the run box's meter maxes out in the
   game, so the cap lands where the player can already see it coming.

   THE SCALE. With the cap the raw numbers are tiny - a median blow of 3 - and
   a damage number of 3 on screen reads as nothing. Seven puts the median blow
   at 21, which is exactly where Tri-Peaks' sits, so STRIKE_TIERS and every
   heal and guard priced off BLOW_AVG keep working untouched.

   WHICH BOARDS COUNT. The monster's health is priced on boards that do NOT
   clear, because a board that clears ends the fight whatever its damage -
   pricing on all boards would set the health from the 29% that were already
   over. And on their MEDIAN rather than their average, because the average is
   pulled up by boards that were nearly wins, and a health only a good board
   can reach means losing eleven boards and then winning one. */
const CAP_OUT = 8, SCALE_OUT = 7;
const lostD = [], outBlows = [], outBreaks = [], outSuits = [];
let clears = 0;
for(let n = 0; n < GAMES; n++){
  const r = play(deal(), 400, { runCap: CAP_OUT });
  if(r.won){ clears++; continue; }
  let tot = 0;
  for(const [len, val] of r.chains){
    const w = val * len * SCALE_OUT;
    tot += w; outBlows.push(w);
  }
  lostD.push(tot); outBreaks.push(r.chains.length); outSuits.push(r.suits);
}
lostD.sort((a, b) => a - b); outBlows.sort((a, b) => a - b);
const BA = Math.round(avg(outBlows));
const RM = Math.round(p(lostD, .5));
const SH = +avg(outSuits).toFixed(2), CR = +(clears / GAMES).toFixed(2);
const bonus = SH * Math.round(1.2 * BA) + CR * Math.round(4 * BA);

console.log();
console.log(`  FIGHT.klondike  (run capped at ${CAP_OUT}, blow scaled by ${SCALE_OUT})`);
console.log(`    ROUND_AVG: ${RM}, ROUND_MED: ${RM},   /* the median board that does not clear */`);
console.log(`    STRIKES: ${avg(outBreaks).toFixed(2)},`);
console.log(`    BLOW_AVG: ${BA}, BLOW_MED: ${Math.round(p(outBlows, .5))}, BLOW_P90: ${Math.round(p(outBlows, .9))},`);
console.log(`    DOWN_AVG: ${SH}, CLEAR_RATE: ${CR},`);
console.log(`    RUN_CAP: ${CAP_OUT}, SCALE: ${SCALE_OUT},`);
console.log();
console.log(`    a board that does not clear deals ${avg(lostD).toFixed(0)} avg / ${RM} median`);
console.log(`    so roundDamage(1) is ${RM} + ${bonus.toFixed(0)} = ${(RM + bonus).toFixed(0)}`);
const hp = Math.round((RM + bonus) / 1.15 / 50) * 50;
const kills = lostD.filter(d => d >= hp).length;
console.log(`    monster health at level 1, even kind = ${hp}`);
console.log(`    boards that end the fight         : ${(100 * (kills + clears) / GAMES).toFixed(0)}% (${(100 * clears / GAMES).toFixed(0)}% by clearing)`);
console.log(`    so a fight runs                   : ${(GAMES / (kills + clears)).toFixed(2)} boards`);
console.log(`    HURT_SHARE .3 then costs the hero : ${Math.round(Math.max(5, Math.round(400 * .3 / avg(outBreaks) / 5) * 5) * avg(outBreaks) * GAMES / (kills + clears))} of 400`);
