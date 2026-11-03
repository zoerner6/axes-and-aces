/* Does a Klondike Monster Solitaire fight come out fair?
     node dev/gen/klbalance.cjs [fights per case]

   The same job dev/gen/slbalance.cjs does for Tri-Peaks, and built the same
   way: whole fights, with the real formulas lifted out of dev/solitaire.html
   through dev/gen/slfight.cjs so this cannot drift from the game, and with the
   real board required from dev/gen/klondike.cjs so the deal cannot drift from
   the one the damage was measured on.

   The player is the deliberately ordinary one klondike.cjs measures with, who
   wins 29% of boards. Not a solver: building the fight on perfect play would
   make every fight too hard for everyone who is not one.

   WHAT TO LOOK FOR, and it is not the same shape as Tri-Peaks. Klondike is all
   or nothing - you either break the board open and send all 52 home or you jam
   and send 13 - so a fight is not reliably one board the way a Tri-Peaks fight
   is. What matters is that a bare hero at their own level wins most fights and
   finishes bloodied rather than untouched, that the median fight is one or two
   boards rather than eleven, and that a boss is harder than an ordinary
   monster. A win rate near 100% with most of the hero's health left means the
   monster's health is too low, however good the fight felt once. */
const path = require('path');
process.chdir(path.join(__dirname, '..', '..'));
const K = require('./klondike.cjs');
/* KL_ROUND_AVG=500 node dev/gen/klbalance.cjs sweeps the monster's health
   without touching the game, which is how the number in the table was chosen. */
const OVER = {};
if(process.env.KL_ROUND_AVG) OVER.ROUND_AVG = +process.env.KL_ROUND_AVG;
const F = require('./slfight.cjs')('klondike', OVER);

const FIGHTS = +(process.argv[2] || 4000);
const CAP = 12;                              /* boards before calling it a draw */

/* One whole fight. Gear is flat Attack and Defense points, as in slbalance. */
function fight(L, atkPts, defPts, boss, area, rule = {}){
  const a = F.WORLDS[0].areas[area];
  const kind = boss ? a.boss : a.pool[Math.random() * a.pool.length | 0];
  const d = F.makeFoe(kind, L, boss);
  let fhp = d.hp, fblk = 0, mv = 0;
  let hp = F.heroMaxHP(L), boards = 0, strikes = 0, best = 0, clearKill = 0;
  const lm = F.lvlMult(L), am = 1 + atkPts / 100;
  const take = n => Math.max(1, Math.round(n / (1 + defPts / 100)));
  const atks = d.moves.filter(m => m.k === 'atk');
  const dryHit = Math.round(atks.reduce((x, y) => x + y.n, 0) / Math.max(1, atks.length) * F.DRY_MULT);

  /* the monster's scheduled answer to a strike */
  const answer = () => {
    const m = d.moves[mv++ % d.moves.length];
    if(m.k === 'atk') hp -= take(m.n);
    else if(m.k === 'blk') fblk += m.n;
    else fhp = Math.min(d.hp, fhp + m.n);
  };

  while(fhp > 0 && hp > 0 && boards < CAP){
    boards++;
    const g = K.deal(Math.random, { deeper: rule.deeper });
    const r = K.play(g, 400, { runCap: rule.cap || F.RUN_CAP, passes: rule.passes });

    for(let i = 0; i < r.chains.length; i++){
      const [len, val] = r.chains[i];
      /* the blow the game lands: runVal * run, carrying the board's scale */
      const dmg = F.armored(Math.round(val * len * F.SCALE * lm * am), d);
      const abs = Math.min(fblk, dmg); fblk -= abs;
      fhp -= dmg - abs;
      strikes++;
      if(len > best) best = len;
      if(fhp <= 0) break;
      /* the last run of a cleared board is not answered: clearing is already
         the reward, which is what doStrike({answer:false}) does in the game */
      const last = i === r.chains.length - 1;
      if(!(last && r.cleared)) answer();
      if(hp <= 0) break;
    }
    if(fhp <= 0 || hp <= 0) break;

    /* what a board pays on top of its runs: one per finished suit, and a much
       bigger one for getting the whole deck home */
    const bonus = r.suits * F.PEAK_BONUS + (r.cleared ? F.CLEAR_BONUS : 0);
    if(bonus) fhp -= F.armored(Math.round(bonus * lm * am), d);
    if(fhp <= 0){ if(r.cleared) clearKill = 1; break; }

    if(!r.cleared) hp -= take(dryHit);      /* ran out of deck with cards still down */
  }
  return { win: fhp <= 0 && hp > 0, boards, strikes, best, clearKill,
           left: Math.max(0, hp) / F.heroMaxHP(L) };
}

function run(label, n, ...args){
  let wins = 0, boards = 0, strikes = 0, left = 0, best = 0, ck = 0;
  const bh = [];
  for(let i = 0; i < n; i++){
    const r = fight(...args);
    if(r.win){ wins++; left += r.left; ck += r.clearKill; }
    boards += r.boards; strikes += r.strikes; best = Math.max(best, r.best);
    bh.push(r.boards);
  }
  bh.sort((x, y) => x - y);
  console.log(`  ${label.padEnd(36)} win ${(100 * wins / n).toFixed(0).padStart(3)}%   ` +
    `boards ${(boards / n).toFixed(2)} (median ${bh[n >> 1]})   ` +
    `strikes ${(strikes / n).toFixed(1)}   ` +
    `health left ${wins ? (100 * left / wins).toFixed(0) : 0}%   ` +
    `killed by a clear ${wins ? (100 * ck / wins).toFixed(0) : 0}%`);
}

console.log(`Klondike Monster Solitaire, ${FIGHTS} fights a case.`);
console.log(`ROUND_AVG ${F.ROUND_AVG}  BLOW_AVG ${F.BLOW_AVG}  STRIKES ${F.STRIKES}  ` +
  `RUN_CAP ${F.RUN_CAP}  SCALE ${F.SCALE}  HURT_SHARE ${F.HURT_SHARE}  DRY_MULT ${F.DRY_MULT}\n`);

console.log('a bare hero, no gear:');
for(const L of [1, 3, 5, 8, 12, 20])
  run(`level ${L}, own level`, FIGHTS, L, 0, 0, false, Math.min(3, (L / 3) | 0));

console.log('\ngeared, as a player who shops would be:');
run('level 5, tin axe and tin armor', FIGHTS, 5, 28, 30, false, 1);
run('level 12, steel axe and steel kit', FIGHTS, 12, 75, 190, false, 3);

/* Every one of Klondike's four boss rules changes what can be PLAYED, which is
   the difference from Tri-Peaks: two of its four changed only what could be
   SEEN, and a bot that never plans a route cannot feel those at all. Burying a
   column deeper, taking passes away and capping the run all cost a bot exactly
   what they cost a person, so all four of these numbers mean something. */
console.log('\nevery lever, level 6, same gear, same monster - how the four were chosen:');
run('an ordinary deal', FIGHTS, 6, 20, 20, true, 1);
run('a run cannot pass five', FIGHTS, 6, 20, 20, true, 1, { cap: 5 });
run('the deck comes round twice', FIGHTS, 6, 20, 20, true, 1, { passes: 2 });
run('the deck comes round once', FIGHTS, 6, 20, 20, true, 1, { passes: 1 });
for(const n of [1, 2, 3])
  run(`the ${n} longest buried deeper`, FIGHTS, 6, 20, 20, true, 1, { deeper: n });
run('two buried deeper, deck round once', FIGHTS, 6, 20, 20, true, 1, { deeper: 2, passes: 1 });

/* and the four the game ships, each at its own area's boss, with the gear and
   the level a player would plausibly have reached by then */
console.log('\nthe four bosses as they are met:');
F.BOSS_RULES.forEach((r, i) =>
  run(`area ${i + 1}: ${r.text}`, FIGHTS, 6 + i * 2, 20 + i * 10, 20 + i * 10, true, i, r.deal));
