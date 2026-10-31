/* Build the scene -> prompt list for the animated story scenes. */
const fs=require('fs'), path=require('path');
const root=path.join(__dirname,'..','..');
const s=fs.readFileSync(path.join(root,'dev/game.html'),'utf8');
const WORLDS=eval(s.match(/const WORLDS = (\[[\s\S]*?\]);/)[1]);
const STORIES=eval('('+s.match(/let STORIES = (\{[\s\S]*?\n\};)/)[1].replace(/;$/,'')+')');

const map={};
['start','a1','a2','a3','end'].forEach(k=>(STORIES[k]||[]).forEach((p,i)=>{ map[k+'_'+i]={title:p.title,text:p.text}; }));
WORLDS.forEach(W=>{
  const pre=W.id+'_';
  (W.intro||[]).forEach((p,i)=>{ map[pre+'start_'+i]={title:p.title,text:p.text}; });
  const st=W.story||{};
  (st.end||[]).forEach((p,i)=>{ map[pre+'end_'+i]={title:p.title,text:p.text}; });
  ['a1','a2','a3'].forEach(k=>{ if(st[k]) map[pre+k+'_0']={title:st[k].title,text:st[k].text}; });
});
module.exports={map,WORLDS,STORIES};
if(require.main===module){
  const all=fs.readdirSync(path.join(root,'art')).filter(f=>/^sc_.*\.webp$/.test(f)).map(f=>f.replace(/^sc_|\.webp$/g,''));
  const have=fs.readdirSync(path.join(root,'vid')).filter(f=>/^sc_.*\.mp4$/.test(f)).map(f=>f.replace(/^sc_|\.mp4$/g,''));
  const todo=all.filter(x=>!x.startsWith('find_')&&!have.includes(x));
  const miss=todo.filter(t=>!map[t]);
  console.log('scene keys from story data:',Object.keys(map).length);
  console.log('to animate:',todo.length,' matched:',todo.length-miss.length,' unmatched:',miss.length);
  if(miss.length) console.log('UNMATCHED:',miss.join(' '));
  fs.writeFileSync(path.join(__dirname,'out','todo.json'),JSON.stringify(todo));
  fs.writeFileSync(path.join(__dirname,'out','scenes.json'),JSON.stringify(map,null,1));
}
