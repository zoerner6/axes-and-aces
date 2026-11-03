/* What a Monster Farkle turn is actually worth.
     node dev/gen/dieavg.cjs [turns]

   Monster health and monster hits have to be built off a measured number, not
   a guessed one - the way HAND_AVG in dev/game.html was measured by
   dev/gen/handavg.cjs. This runs the real scoring code, lifted straight out of
   dev/farkle.html so there is only ever one copy of the rules, checks it
   against every case worth checking, then plays a few hundred thousand turns
   and reports what a turn delivers.

   It also sweeps the bank-at threshold, because "what a turn is worth" depends
   on how greedy the player is, and the number that belongs in the game is the
   one a player who has worked the game out would get. */
const fs = require('fs');
const path = require('path');
process.chdir(path.join(__dirname, '..', '..'));

/* ---- lift the scoring out of the game ---- */
const src = fs.readFileSync('dev/farkle.html', 'utf8');
const block = src.match(/\/\* ===== SCORING [\s\S]*?\/\* ===== END SCORING ===== \*\//);
if (!block) { console.error('Could not find the SCORING block in dev/farkle.html'); process.exit(1); }
const F = {};
new Function('X', block[0] + '\nObject.assign(X,{counts,scoreOf,scoreSet,bestSplit,isFarkle,reachable,namedCombos,FACE3});')(F);
console.log(`Lifted the scoring block out of dev/farkle.html (${block[0].length} characters).\n`);

/* ---- check it ---- */
const cases = [
  [[1, 2, 3, 4, 5, 6], 1500, 'straight'],
  [[2, 2, 3, 3, 4, 4], 1500, 'three pairs'],
  [[1, 1, 1, 5, 5, 5], 2500, 'two triplets beats 1000 + 500'],
  [[6, 6, 6, 5, 5, 5], 2500, 'two triplets'],
  [[3, 3, 3, 3, 6, 6], 1500, 'four of a kind plus a pair'],
  [[1, 1, 1, 1, 5, 5], 2100, 'four 1s doubled, plus two 5s, beats four-plus-pair'],
  [[1, 1, 1], 1000, 'three 1s'],
  [[1, 1, 1, 1], 2000, 'four 1s double'],
  [[1, 1, 1, 1, 1], 4000, 'five 1s double again'],
  [[1, 1, 1, 1, 1, 1], 8000, 'six 1s, the jackpot'],
  [[6, 6, 6], 600, 'three 6s'],
  [[6, 6, 6, 6], 1200, 'four 6s double'],
  [[2, 2, 2], 200, 'three 2s'],
  [[1], 100, 'one 1'],
  [[5], 50, 'one 5'],
  [[1, 5], 150, 'a 1 and a 5'],
  [[2, 3, 4, 6], null, 'nothing scores, and no die can be kept'],
  [[2, 2], null, 'a bare pair is not legal to keep'],
  [[1, 2], null, 'the 2 is dead weight, so keeping both is illegal'],
];
let fails = 0;
for (const [faces, want, why] of cases) {
  const got = F.scoreOf(faces);
  const ok = got === want;
  if (!ok) fails++;
  console.log(`${ok ? '  ok  ' : 'FAIL  '}${String(faces.join('-')).padEnd(13)} ${String(got).padStart(5)}  want ${String(want).padStart(5)}  ${why}`);
}
/* a farkle is a roll where the best split is worth nothing */
const farkleCases = [[[2, 3, 4, 6], true], [[2, 2, 3, 3], true], [[1, 2, 3], false], [[2, 2, 2], false], [[3, 3, 4, 4, 6, 6], false]];
for (const [faces, want] of farkleCases) {
  const got = F.isFarkle(faces);
  if (got !== want) { fails++; console.log(`FAIL  isFarkle(${faces.join('-')}) = ${got}, want ${want}`); }
}
/* three pairs is six dice only: the same four dice in a roll of four is a farkle */
if (F.scoreOf([2, 2, 3, 3]) !== null) { fails++; console.log('FAIL  two pairs out of four dice should not be legal'); }
console.log(fails ? `\n${fails} checks FAILED.\n` : '\nAll scoring checks pass.\n');
if (fails) process.exit(1);

/* ---- play a lot of turns ----
   The player keeps the best split, then banks once the wind-up reaches the
   threshold, except that hot dice are always rolled - six fresh dice can only
   farkle 2.3% of the time, so declining them is never right. */
const roll = n => { const f = []; for (let i = 0; i < n; i++) f.push(1 + (Math.random() * 6 | 0)); return f; };

function turn(bankAt) {
  let wind = 0, live = 6, rolls = 0;
  for (;;) {
    const faces = roll(live);
    rolls++;
    const b = F.bestSplit(faces);
    if (b.score === 0) return { points: 0, farkled: true, rolls };
    wind += b.score;
    live -= b.keep.length;
    if (live === 0) live = 6;                 /* hot dice: all six come back */
    else if (wind >= bankAt) return { points: wind, farkled: false, rolls };
  }
}

const N = +(process.argv[2] || 400000);
const rows = [];
for (const bankAt of [250, 300, 350, 400, 450, 500, 600, 700, 800, 1000, 1250, 1500]) {
  let total = 0, farkles = 0, banked = 0, bankedSum = 0, rolls = 0, best = 0;
  for (let i = 0; i < N; i++) {
    const t = turn(bankAt);
    total += t.points; rolls += t.rolls;
    if (t.farkled) farkles++; else { banked++; bankedSum += t.points; if (t.points > best) best = t.points; }
  }
  rows.push({ bankAt, per: total / N, farkle: farkles / N, avgBank: bankedSum / banked, rolls: rolls / N, best });
}
console.log(`${N.toLocaleString('en-US')} turns at each threshold:\n`);
console.log('bank at   per turn   farkle rate   when banked   rolls/turn   biggest');
for (const r of rows)
  console.log(`${String(r.bankAt).padStart(7)}   ${r.per.toFixed(1).padStart(8)}   ${(r.farkle * 100).toFixed(1).padStart(10)}%   ${r.avgBank.toFixed(0).padStart(11)}   ${r.rolls.toFixed(2).padStart(10)}   ${String(r.best).padStart(7)}`);

const best = rows.reduce((a, b) => (b.per > a.per ? b : a));
console.log(`\nBest threshold: bank at ${best.bankAt}.`);
console.log(`  A turn delivers ${best.per.toFixed(0)} on average, counting farkles as nothing.`);
console.log(`  ${(best.farkle * 100).toFixed(0)}% of turns farkle.`);
console.log(`  When a turn does bank it banks ${best.avgBank.toFixed(0)}.`);
console.log(`\nWINDUP_AVG = ${Math.round(best.per / 5) * 5}   <- the number the fight maths is built on.`);
