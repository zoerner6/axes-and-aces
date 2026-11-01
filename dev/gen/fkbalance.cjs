/* Does a Monster Farkle fight come out fair?
     node dev/gen/fkbalance.cjs [fights per level]

   Plays whole fights with the real scoring and the real formulas, both lifted
   out of dev/farkle.html so this cannot drift from the game. The player is a
   reasonable one, not a perfect one: keeps the best split, banks once the
   wind-up is worth more than the risk, and always takes hot dice.

   What to look for: a bare hero with no gear and no potions should win most
   fights and still finish bloodied, in five to eight turns. Too short and the
   push-your-luck never bites; too long and one bad farkle run kills a fight
   the player was winning. */
const fs = require('fs');
const path = require('path');
process.chdir(path.join(__dirname, '..', '..'));

const src = fs.readFileSync('dev/farkle.html', 'utf8');
const lift = (a, b) => {
  const m = src.match(new RegExp(`\\/\\* ===== ${a}[\\s\\S]*?\\/\\* ===== ${b} ===== \\*\\/`));
  if (!m) { console.error(`Could not find the ${a} block in dev/farkle.html`); process.exit(1); }
  return m[0];
};
const F = {};
new Function('X', 'WINDUP_AVG',
  lift('SCORING', 'END SCORING') + '\n' + lift('THE FIGHT MATHS', 'END FIGHT MATHS') +
  '\nObject.assign(X,{bestSplit,isFarkle,scoreOf,genMonster,monsterHP,foeHit,foeArmorFor,armored,' +
  'heroMaxHP,lvlMult,turnDamage,temper,WORLDS,TURNS,FARKLE_MULT,EQUIP});'
)(F, +src.match(/const WINDUP_AVG = (\d+)/)[1]);

const roll = n => { const f = []; for (let i = 0; i < n; i++) f.push(1 + (Math.random() * 6 | 0)); return f; };

/* One of the player's turns: returns what was banked, or 0 on a farkle. */
function playerTurn(bankAt) {
  let wind = 0, live = 6;
  for (;;) {
    const faces = roll(live);
    const b = F.bestSplit(faces);
    if (!b.score) return 0;
    wind += b.score;
    live -= b.keep.length;
    if (live === 0) live = 6;
    else if (wind >= bankAt) return wind;
  }
}

/* One whole fight. Gear is given as flat Attack and Defense points. */
function fight(L, atkPts, defPts, bankAt, cap = 60, boss = false, area = 0) {
  const a = F.WORLDS[0].areas[area];
  const kind = boss ? a.boss : a.pool[Math.random() * a.pool.length | 0];
  const d = F.genMonster(kind, L, boss);
  let fhp = d.hp, fblk = 0, mv = 0;
  let hp = F.heroMaxHP(L), turns = 0;
  const lm = F.lvlMult(L), am = 1 + atkPts / 100;
  const take = n => Math.max(1, Math.round(n / (1 + defPts / 100)));
  const atks = d.moves.filter(m => m.k === 'atk');
  const farkleHit = Math.round(atks.reduce((a, b) => a + b.n, 0) / Math.max(1, atks.length) * F.FARKLE_MULT);
  while (fhp > 0 && hp > 0 && turns < cap) {
    turns++;
    const w = playerTurn(bankAt);
    if (w) {
      const dmg = F.armored(Math.round(w * lm * am), d);
      const soak = Math.min(fblk, dmg); fblk -= soak; fhp -= dmg - soak;
      if (fhp <= 0) break;
      const m = d.moves[mv++ % d.moves.length];
      if (m.k === 'atk') hp -= take(m.n);
      else if (m.k === 'blk') fblk += m.n;
      else fhp = Math.min(d.hp, fhp + m.n);
    } else {
      hp -= take(farkleHit);
    }
  }
  return { won: fhp <= 0 && hp > 0, turns, hpLeft: Math.max(0, hp), maxHp: F.heroMaxHP(L), name: d.name, timeout: turns >= cap };
}

const N = +(process.argv[2] || 4000);
const GEAR = [
  ['bare hands, no armor', 0, 0],
  ['first tier gear', F.EQUIP.sword.atk[1] + F.EQUIP.dagger.atk[1], F.EQUIP.shield.def[1] + F.EQUIP.helm.def[1] + F.EQUIP.armor.def[1]],
  ['third tier gear', F.EQUIP.axe.atk[3], F.EQUIP.shield.def[3] + F.EQUIP.helm.def[3] + F.EQUIP.armor.def[3]],
];
console.log(`Lifted the scoring and the fight maths out of dev/farkle.html.`);
console.log(`TURNS target = ${F.TURNS}, farkle costs x${F.FARKLE_MULT}.\n`);
for (const [label, atk, def] of GEAR) {
  console.log(`${label}  (Attack +${atk}, Defense +${def})`);
  console.log('  level   win rate   turns   health left   timeouts');
  for (const L of [1, 2, 3, 5, 8, 12]) {
    let wins = 0, turns = 0, left = 0, to = 0;
    for (let i = 0; i < N; i++) {
      const r = fight(L, atk, def, 300);
      if (r.won) { wins++; left += r.hpLeft / r.maxHp; }
      turns += r.turns;
      if (r.timeout) to++;
    }
    console.log(`  ${String(L).padStart(5)}   ${(wins / N * 100).toFixed(0).padStart(7)}%   ${(turns / N).toFixed(1).padStart(5)}   ${wins ? (left / wins * 100).toFixed(0).padStart(10) + '%' : '         -'}   ${String(to).padStart(8)}`);
  }
  console.log('');
}
/* a boss should be longer and harder than a normal fight, not a wall */
console.log('bosses, first tier gear, at the level you meet them:');
console.log('  area   win rate   turns   health left');
for (const [area, L] of [[0, 3], [1, 5], [2, 7], [3, 9]]) {
  let wins = 0, turns = 0, left = 0;
  const atk = F.EQUIP.sword.atk[2] + F.EQUIP.dagger.atk[2];
  const def = F.EQUIP.shield.def[2] + F.EQUIP.helm.def[2] + F.EQUIP.armor.def[2];
  for (let i = 0; i < N; i++) {
    const r = fight(L, atk, def, 350, 60, true, area);
    if (r.won) { wins++; left += r.hpLeft / r.maxHp; }
    turns += r.turns;
  }
  console.log(`  ${String(area + 1).padStart(4)}   ${(wins / N * 100).toFixed(0).padStart(7)}%   ${(turns / N).toFixed(1).padStart(5)}   ${wins ? (left / wins * 100).toFixed(0).padStart(10) + '%' : '         -'}`);
}
console.log('');

/* how much the bank-at choice matters inside a real fight */
console.log('bare hands at level 1, by how greedy the player is:');
console.log('  bank at   win rate   turns');
for (const b of [200, 250, 300, 400, 500, 700, 1000]) {
  let wins = 0, turns = 0;
  for (let i = 0; i < N; i++) { const r = fight(1, 0, 0, b); if (r.won) wins++; turns += r.turns; }
  console.log(`  ${String(b).padStart(7)}   ${(wins / N * 100).toFixed(0).padStart(7)}%   ${(turns / N).toFixed(1).padStart(5)}`);
}
