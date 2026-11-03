/* The fight maths, lifted out of dev/solitaire.html for whichever board you
   ask for.

     const F = require('./slfight.cjs')('klondike');
     F.monsterHP(1, 1, 15)

   There are two boards now, and one set of constants became two. Before that,
   dev/gen/slbalance.cjs read each number with a `const NAME = 123` regex
   straight out of the file. That stopped working the moment the numbers moved
   into the FIGHT table, and it would have stopped silently if the regex had
   happened to match something else - which is the whole reason this exists in
   one place instead of in each tool.

   Nothing here is a copy. The FIGHT table and the derivation of PEAK_BONUS,
   CLEAR_BONUS and BONUS_AVG are evaluated from the file's own source, and the
   maths block is run from the file's own source, so a change to the game is a
   change here and a tool that disagrees with the game cannot exist. */
const fs = require('fs');
const path = require('path');

const FILE = path.join(__dirname, '..', 'solitaire.html');

function slice(src, from, to){
  const i = src.indexOf(from);
  if(i < 0) throw new Error(`slfight: could not find ${JSON.stringify(from)} in dev/solitaire.html`);
  const j = src.indexOf(to, i);
  if(j < 0) throw new Error(`slfight: could not find ${JSON.stringify(to)} after it`);
  return src.slice(i, j + to.length);
}

/* `over` replaces individual constants after the table is read, so a tuning
   tool can sweep a number without editing the game and then put the one it
   settles on into the table by hand. Everything derived from it - the bonuses,
   the monster's health, its hit - follows on its own. */
module.exports = function slfight(board = 'klondike', over = {}){
  const src = fs.readFileSync(FILE, 'utf8');

  /* the table and the three bonuses derived from it, run as the game runs them */
  const table = slice(src, 'const FIGHT = {', "useBoard('klondike');");
  const C = new Function(table + `
    useBoard(${JSON.stringify(board)});
    return { ROUND_AVG, ROUND_MED, STRIKES, BLOW_AVG, BLOW_MED, BLOW_P90,
             DOWN_AVG, CLEAR_RATE, RUN_CAP, SCALE, HURT_SHARE,
             PEAK_BONUS, CLEAR_BONUS, BONUS_AVG };`)();
  const F0 = {};
  if(C.ROUND_AVG == null) throw new Error(`slfight: no board called ${board}`);
  Object.assign(C, over);
  if(over.BLOW_AVG != null || over.DOWN_AVG != null || over.CLEAR_RATE != null){
    C.PEAK_BONUS  = Math.round(1.2 * C.BLOW_AVG);
    C.CLEAR_BONUS = Math.round(4 * C.BLOW_AVG);
    C.BONUS_AVG   = C.DOWN_AVG * C.PEAK_BONUS + C.CLEAR_RATE * C.CLEAR_BONUS;
  }

  /* the maths itself, which reads those as bare names - so they go in as
     arguments rather than being redeclared, exactly as the game has them */
  /* the board's own boss rules, so a tool measures the four the game ships
     rather than four it was told about */
  const rules = slice(src, 'const BOSS_RULE_SETS = {', '};');
  F0.BOSS_RULES = new Function(rules + `
    return BOSS_RULE_SETS[${JSON.stringify(board)}];`)();

  const maths = slice(src, '/* ===== THE FIGHT MATHS', '/* ===== END FIGHT MATHS ===== */');
  const names = ['ROUND_AVG', 'ROUND_MED', 'STRIKES', 'BLOW_AVG', 'BLOW_MED', 'BLOW_P90',
                 'DOWN_AVG', 'CLEAR_RATE', 'RUN_CAP', 'SCALE', 'HURT_SHARE',
                 'PEAK_BONUS', 'CLEAR_BONUS', 'BONUS_AVG'];
  const F = Object.assign(F0, { board }, C);
  new Function('X', ...names, maths + `
    Object.assign(X, { makeFoe, monsterHP, foeHit, foeArmorFor, foeArmor, armored,
      heroMaxHP, lvlMult, roundDamage, blowDamage, temper, WORLDS, ROUNDS, DRY_MULT });`
  )(F, ...names.map(n => C[n]));
  return F;
};
