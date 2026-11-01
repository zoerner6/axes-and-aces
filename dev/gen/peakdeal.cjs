/* What a Tri-Peaks deal is actually worth.
   node dev/gen/peakdeal.cjs [--deals 200000] [--solve 20000]

   Monster Solitaire scales monster health and monster hits off a real player's
   output, the way dev/gen/handavg.cjs measured HAND_AVG = 121 for the card
   game. Guessing these numbers would make every fight in the game wrong at
   once, so they get measured here and pasted into dev/solitaire.html.

   Two separate questions, two separate runs:

   1. How many random deals can be cleared at all? Tri-Peaks deals vary wildly
      and a dead board is not a fight, it is a bad gift. If the share is low,
      the deal gets biased: reshuffle until a solver says it is clearable, so a
      player never opens a round that cannot be won. That needs an exact
      solver, which is slow, so it runs on fewer deals.

   2. What does an ordinary player get out of a solvable deal? That is the
      number the damage is built on, and it is NOT what the solver gets - the
      solver plays perfectly and a person does not. So a deliberately ordinary
      greedy player is simulated instead, on many more deals.

   The layout is the standard 28-card tableau: 3 peak tips, then 6, then 9,
   then a face-up row of 10, with 24 cards left in the stock. */

const args = process.argv.slice(2);
const flag = (n, d) => { const i = args.indexOf(n); return i >= 0 ? +args[i + 1] : d; };
const DEALS = flag('--deals', 200000);
const SOLVE = flag('--solve', 20000);

/* ---------- the layout ----------
   Indices 0-2 are the three peak tips, 3-8 the second row, 9-17 the third,
   18-27 the face-up bottom row. A card is playable once both cards covering
   it are gone; the bottom row is covered by nothing. */
const COVERS = (() => {
  const c = Array.from({ length: 28 }, () => []);
  c[0] = [3, 4]; c[1] = [5, 6]; c[2] = [7, 8];
  for (let p = 0; p < 3; p++) {
    const r2 = 3 + p * 2, r3 = 9 + p * 3;
    c[r2] = [r3, r3 + 1];
    c[r2 + 1] = [r3 + 1, r3 + 2];
  }
  for (let i = 0; i < 9; i++) c[9 + i] = [18 + i, 18 + i + 1];
  return c;
})();

/* which peak each tableau card belongs to, for "peak down" */
const PEAK = (() => {
  const p = new Array(28).fill(-1);
  for (let k = 0; k < 3; k++) {
    p[k] = k;
    p[3 + k * 2] = k; p[4 + k * 2] = k;
    p[9 + k * 3] = k; p[10 + k * 3] = k; p[11 + k * 3] = k;
  }
  return p;                      /* the bottom row stays -1: it is shared */
})();

/* ---------- cards ----------
   Rank 1 is an ace. Aces wrap both ways, so the ranks are a ring of 13 and a
   king takes an ace. Value is what the card is worth to a run: its own number,
   with the faces above ten and the ace highest, because an ace is the most
   useful card on the board and should pay like it. */
const VALUE = r => (r === 1 ? 14 : r);    /* A=14, K=13, Q=12, J=11, the rest their own number */
const takes = (a, b, wrap) => {
  const d = Math.abs(a - b);
  return d === 1 || (wrap && d === 12);
};

function deal(rnd) {
  const d = [];
  for (let s = 0; s < 4; s++) for (let r = 1; r <= 13; r++) d.push(r);
  for (let i = d.length - 1; i > 0; i--) {
    const j = (rnd() * (i + 1)) | 0;
    [d[i], d[j]] = [d[j], d[i]];
  }
  return { tableau: d.slice(0, 28), stock: d.slice(28) };   /* 28 + 24 */
}

const exposed = (mask, i) => !(mask & (1 << i)) && COVERS[i].every(c => mask & (1 << c));
const FULL = (1 << 28) - 1;

/* ---------- the exact solver ----------
   State is the set of cleared cards, how far into the stock we are, and the
   card showing on the waste. The stock turns in a fixed order, so those three
   are the whole state and it memoizes cleanly. Capped, because a handful of
   deals explode and an answer for 99.9% of them beats hanging on one. */
function solvable(t, stock, wrap, cap = 300000) {
  const seen = new Set();
  let budget = cap;
  const go = (mask, si, top) => {
    if (mask === FULL) return true;
    if (--budget < 0) return null;                 /* gave up, not "no" */
    const key = mask * 350 + si * 14 + top;
    if (seen.has(key)) return false;
    seen.add(key);
    for (let i = 0; i < 28; i++) {
      if (exposed(mask, i) && takes(t[i], top, wrap)) {
        const r = go(mask | (1 << i), si, t[i]);
        if (r !== false) return r;
      }
    }
    if (si < stock.length) {
      const r = go(mask, si + 1, stock[si]);
      if (r !== false) return r;
    }
    return false;
  };
  return go(0, 1, stock[0]);                       /* first stock card starts the waste */
}

/* ---------- an ordinary player ----------
   Deliberately not clever. Always plays a card rather than turning one, and
   among the playable cards takes the one that frees the most new cards,
   leaning towards the peaks when that ties. A real person plays roughly this
   well and no better; building the damage on the solver's play would make
   every fight too easy for everybody who is not a solver. */
function greedy(t, stock, wrap) {
  let mask = 0, si = 1, top = stock[0];
  let run = 0, best = 0, runVal = 0, bestVal = 0, turns = 0;
  const runs = [];
  for (;;) {
    let pick = -1, pickScore = -1;
    for (let i = 0; i < 28; i++) {
      if (!exposed(mask, i) || !takes(t[i], top, wrap)) continue;
      const m2 = mask | (1 << i);
      let frees = 0;
      for (let j = 0; j < 28; j++) if (!exposed(mask, j) && exposed(m2, j)) frees++;
      const score = frees * 10 + (i < 18 ? (18 - i) / 18 : 0);
      if (score > pickScore) { pickScore = score; pick = i; }
    }
    if (pick >= 0) {
      mask |= (1 << pick); top = t[pick];
      run++; runVal += VALUE(t[pick]);
      if (mask === FULL) break;
      continue;
    }
    if (run) { runs.push([run, runVal]); if (run > best) { best = run; bestVal = runVal; } }
    run = 0; runVal = 0;
    if (si >= stock.length) break;                 /* dry, with peaks still up */
    top = stock[si++]; turns++;
  }
  if (run) { runs.push([run, runVal]); if (run > best) { best = run; bestVal = runVal; } }
  /* The blow a run lands is its total value times its length, so the damage a
     whole round produces is that summed over every run in it. This is the
     number monster health gets built on. */
  const damage = runs.reduce((a, [len, val]) => a + val * len, 0);
  return {
    cleared: mask === FULL,
    best, bestVal, turns, damage,
    cards: 28 - popcount(~mask & FULL),
    stockLeft: stock.length - si,
    down: [0, 1, 2].filter(p => {
      for (let i = 0; i < 18; i++) if (PEAK[i] === p && !(mask & (1 << i))) return false;
      return true;
    }).length,
    runs,
  };
}

/* ---------- run it ---------- */
const pct = (a, b) => (100 * a / b).toFixed(1) + '%';
const avg = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;
const popcount = m => { let c = 0; while (m) { m &= m - 1; c++; } return c; };

console.log(`Tri-Peaks: 28 in the tableau, 24 in the stock.`);
console.log(`${SOLVE} deals checked by the exact solver, ${DEALS} played by an ordinary player.
`);

for (const wrap of [true, false]) {
  console.log(`=== aces ${wrap ? 'wrap - ordinary rounds' : 'do not wrap - boss rounds'} ===`);

  let solved = 0, gaveUp = 0;
  for (let n = 0; n < SOLVE; n++) {
    const { tableau, stock } = deal(Math.random);
    const r = solvable(tableau, stock, wrap);
    if (r === true) solved++; else if (r === null) gaveUp++;
  }
  console.log(`  clearable with perfect play : ${pct(solved, SOLVE)}` +
    (gaveUp ? `  (+${pct(gaveUp, SOLVE)} undecided, counted against)` : ''));

  const bests = [], dmg = [], downs = [], left = [], cards = [];
  let clears = 0, dead = 0;
  const hist = new Array(29).fill(0);
  for (let n = 0; n < DEALS; n++) {
    const { tableau, stock } = deal(Math.random);
    const g = greedy(tableau, stock, wrap);
    bests.push(g.best); dmg.push(g.damage); downs.push(g.down); cards.push(g.cards);
    hist[Math.min(28, g.best)]++;
    if (g.cleared) { clears++; left.push(g.stockLeft); }
    if (g.cards < 4) dead++;                 /* a board that gave almost nothing */
  }
  bests.sort((a, b) => a - b); dmg.sort((a, b) => a - b);
  const p = (arr, q) => arr[Math.floor(arr.length * q)];

  console.log(`  an ordinary player clears   : ${pct(clears, DEALS)}`);
  console.log(`  dead boards (under 4 cards) : ${pct(dead, DEALS)}`);
  console.log(`  cards cleared, average      : ${avg(cards).toFixed(1)} of 28`);
  console.log(`  peaks down, average         : ${avg(downs).toFixed(2)} of 3`);
  console.log(`  stock left when cleared     : ${avg(left).toFixed(1)} of 24`);
  console.log(`  longest run  avg/med/90th   : ${avg(bests).toFixed(2)} / ${p(bests, .5)} / ${p(bests, .9)}`);
  console.log(`  ROUND DAMAGE avg/med/90th   : ${avg(dmg).toFixed(0)} / ${p(dmg, .5)} / ${p(dmg, .9)}`);
  const top = hist.map((c, i) => [i, c]).filter(([, c]) => c).slice(0, 14);
  console.log(`  longest-run spread          : ` +
    top.map(([i, c]) => `${i}:${(100 * c / DEALS).toFixed(0)}%`).join('  '));
  console.log();
}
