/* Does a Monster Solitaire fight come out fair?
     node dev/gen/slbalance.cjs [fights per case]

   Plays whole fights with the real formulas, lifted out of dev/solitaire.html
   so this cannot drift from the game, and with the real board, required from
   dev/gen/peakdeal.cjs so the deal cannot drift from the one the damage was
   measured on.

   The player is a reasonable one, not a perfect one: the same deliberately
   ordinary greedy player peakdeal measures with, who clears 47% of boards.

   What to look for. A bare hero with no gear should win most fights at their
   own level and finish bloodied. A fight should usually be one board - that is
   the whole mapping, one reading per monster - with a second board when it
   goes badly, because the second board costs a free heavy swing first. A boss
   is meant to be harder and to take longer, and the no-wrap rule is meant to
   be the hardest of the four. */
const fs = require('fs');
const path = require('path');
process.chdir(path.join(__dirname, '..', '..'));
const P = require('./peakdeal.cjs');

const src = fs.readFileSync('dev/solitaire.html', 'utf8');
const lift = (a, b) => {
  const m = src.match(new RegExp(`\\/\\* ===== ${a}[\\s\\S]*?\\/\\* ===== ${b} ===== \\*\\/`));
  if (!m) { console.error(`Could not find the ${a} block in dev/solitaire.html`); process.exit(1); }
  return m[0];
};
const num = n => +src.match(new RegExp(`const ${n} = (\\d+(?:\\.\\d+)?)`))[1];

const F = {};
new Function('X', 'ROUND_AVG', 'BLOW_AVG', 'STRIKES',
  lift('THE FIGHT MATHS', 'END FIGHT MATHS') +
  '\nObject.assign(X,{makeFoe,monsterHP,foeHit,foeArmorFor,armored,heroMaxHP,lvlMult,' +
  'roundDamage,blowDamage,temper,WORLDS,ROUNDS,DRY_MULT,HURT_SHARE,EQUIP,'+
  'PEAK_BONUS,CLEAR_BONUS,BONUS_AVG});'
)(F, num('ROUND_AVG'), num('BLOW_AVG'), num('STRIKES'));

const FIGHTS = +(process.argv[2] || 4000);
const CAP = 12;                              /* boards before calling it a draw */

/* One whole fight. Gear is flat Attack and Defense points, as in fkbalance. */
function fight(L, atkPts, defPts, boss, area, wrap = true, stockN = 24) {
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
    if (m.k === 'atk') hp -= take(m.n);
    else if (m.k === 'blk') fblk += m.n;
    else fhp = Math.min(d.hp, fhp + m.n);
  };

  while (fhp > 0 && hp > 0 && boards < CAP) {
    boards++;
    const { tableau, stock } = P.deal(Math.random);
    const g = P.greedy(tableau, stock.slice(0, stockN), wrap);
    for (let i = 0; i < g.runs.length; i++) {
      const [len, val] = g.runs[i];
      const dmg = F.armored(Math.round(val * len * lm * am), d);
      const abs = Math.min(fblk, dmg); fblk -= abs;
      fhp -= dmg - abs;
      strikes++;
      if (len > best) best = len;
      if (fhp <= 0) break;
      /* the last run of a cleared board is not answered: clearing is already
         the reward, which is what doStrike({answer:false}) does in the game */
      const last = i === g.runs.length - 1;
      if (!(last && g.cleared)) answer();
      if (hp <= 0) break;
    }
    if (fhp <= 0 || hp <= 0) break;

    /* the bonuses a board pays on top of its runs: one per peak taken down,
       and a much bigger one for cutting the whole reading away */
    const bonus = g.down * F.PEAK_BONUS + (g.cleared ? F.CLEAR_BONUS : 0);
    if (bonus) fhp -= F.armored(Math.round(bonus * lm * am), d);
    if (fhp <= 0) { if (g.cleared) clearKill = 1; break; }

    if (!g.cleared) hp -= take(dryHit);     /* ran the stock dry with peaks up */
  }
  return { win: fhp <= 0 && hp > 0, boards, strikes, best, clearKill,
           left: Math.max(0, hp) / F.heroMaxHP(L) };
}

function run(label, n, ...args) {
  let wins = 0, boards = 0, strikes = 0, left = 0, best = 0, ck = 0;
  const bh = [];
  for (let i = 0; i < n; i++) {
    const r = fight(...args);
    if (r.win) { wins++; left += r.left; ck += r.clearKill; }
    boards += r.boards; strikes += r.strikes; best = Math.max(best, r.best);
    bh.push(r.boards);
  }
  bh.sort((x, y) => x - y);
  console.log(`  ${label.padEnd(34)} win ${(100 * wins / n).toFixed(0).padStart(3)}%   ` +
    `boards ${(boards / n).toFixed(2)} (median ${bh[n >> 1]})   ` +
    `strikes ${(strikes / n).toFixed(1)}   ` +
    `health left ${wins ? (100 * left / wins).toFixed(0) : 0}%   ` +
    `killed by a clear ${wins ? (100 * ck / wins).toFixed(0) : 0}%`);
}

console.log(`Monster Solitaire, ${FIGHTS} fights a case.`);
console.log(`ROUND_AVG ${num('ROUND_AVG')}  BLOW_AVG ${num('BLOW_AVG')}  STRIKES ${num('STRIKES')}  ` +
  `ROUNDS ${F.ROUNDS}  HURT_SHARE ${F.HURT_SHARE}  DRY_MULT ${F.DRY_MULT}\n`);

console.log('a bare hero, no gear:');
for (const L of [1, 3, 5, 8, 12, 20]) run(`level ${L}, own level`, FIGHTS, L, 0, 0, false, Math.min(3, (L / 3) | 0));

console.log('\ngeared, as a player who shops would be:');
run('level 5, tin axe and tin armor', FIGHTS, 5, 28, 30, false, 1);
run('level 12, steel axe and steel kit', FIGHTS, 12, 75, 190, false, 3);

/* A rule only shows up here if it changes what can be PLAYED. Two of the four
   change only what can be SEEN - a peak dealt face down is still playable the
   moment it is uncovered, because a card becomes uncovered and face up at
   exactly the same instant. That is a real difficulty for a person, who can no
   longer plan a route through the board, and it is invisible to a bot, which
   never planned one. So the two face-down rules are NOT measured below, and a
   high win rate against them here means nothing at all. */
console.log('\nwhat each boss rule costs, level 6, same gear, same monster:');
run('an ordinary deal', FIGHTS, 6, 20, 20, true, 1);
run('the stock runs short (18)', FIGHTS, 6, 20, 20, true, 1, true, 18);
run('aces do not wrap', FIGHTS, 6, 20, 20, true, 1, false);
console.log('  (the two face-down rules change only what a player can see,');
console.log('   which a bot never used, so they cannot be measured here)');

console.log('\nbosses as they are actually met:');
run('area 1 boss, one peak face down', FIGHTS, 3, 0, 0, true, 0);
run('area 2 boss, short stock', FIGHTS, 5, 20, 20, true, 1);
run('area 3 boss, two peaks face down', FIGHTS, 7, 40, 50, true, 2);
run('area 4 boss, aces do not wrap', FIGHTS, 9, 50, 70, true, 3, false);
