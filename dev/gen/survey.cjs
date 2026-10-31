/* What art and monsters the game already has. */
const fs = require('fs'), path = require('path');
const s = fs.readFileSync(path.join(__dirname, '..', '..', 'dev', 'game.html'), 'utf8');

const i = s.indexOf('const ART = ');
const j = s.indexOf('};', i);
const ART = eval('(' + s.slice(i + 'const ART = '.length, j + 1) + ')');

const W = eval(s.match(/const WORLDS = (\[[\s\S]*?\]);/)[1]);

const vi = s.indexOf('const VIDS = new Set(');
const VIDS = new Set(eval(s.slice(vi + 'const VIDS = new Set('.length, s.indexOf(');', vi))));

module.exports = { ART, W, VIDS, src: s };

if (require.main === module) {
  console.log('ART entries        :', Object.keys(ART).length);
  console.log('unique art slugs   :', new Set(Object.values(ART)).size);
  console.log('slugs with video   :', VIDS.size);
  let tot = 0; const miss = [];
  W.forEach(w => w.areas.forEach(a => a.pool.forEach(p => {
    tot++; if (!ART[p.name]) miss.push(p.name + ' (' + p.slug + ')');
  })));
  console.log('worlds 2-10 pool   :', tot, 'monsters,', miss.length, 'not in ART');
  if (miss.length) console.log('  e.g.', miss.slice(0, 5).join(', '));
  const noVid = [...new Set(Object.values(ART))].filter(k => !VIDS.has(k));
  console.log('art without video  :', noVid.length, noVid.slice(0, 8).join(' '));
}
