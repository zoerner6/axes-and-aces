/* Keep SCENE_VIDS in step with whatever clips are actually in vid/. */
const fs=require('fs'), path=require('path');
const root=path.join(__dirname,'..','..'), f=path.join(root,'dev/game.html');
const ids=fs.readdirSync(path.join(root,'vid')).filter(x=>/^sc_.*\.mp4$/.test(x)).map(x=>x.replace(/\.mp4$/,'')).sort();
let s=fs.readFileSync(f,'utf8');
const re=/const SCENE_VIDS = new Set\(\[[^\]]*\]\);/;
if(!re.test(s)){ console.error('SCENE_VIDS not found'); process.exit(1); }
s=s.replace(re,'const SCENE_VIDS = new Set(['+ids.map(i=>`'${i}'`).join(',')+']);');
fs.writeFileSync(f,s);
console.log('registered',ids.length,'animated scenes:');
console.log(' ',ids.join(' '));
