const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:760}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8765/site/audit.html');await p.evaluate(()=>{localStorage.clear();localStorage.setItem('tutorialDone','true')});await p.reload();await p.waitForTimeout(1500);
const list=await p.evaluate(()=>window.__A.ev(`(()=>{const L=[];
 ACH.forEach(a=>L.push({key:'ach_'+a.id, eyebrow:'Achievement unlocked', title:a.name, sub:a.desc+' in Axes & Aces.', fig:'art/hero_t3.webp', bg:'art/bg_castle.webp', desc:a.desc}));
 for(let w=0;w<10;w++) loadWorld(w); loadWorld(0); const SEEN={}; Object.entries(ART).filter(([n,k])=>!SEEN[k]&&(SEEN[k]=1)).forEach(([n,k])=>{ const nm=/^The /.test(n)?n.replace(/^The /,'the '):'the '+n; L.push({key:'boss_'+k, eyebrow:'Monster defeated', title:'I defeated '+nm+'!', sub:'A dark comic card adventure. Fight monsters with poker hands.', fig:'art/dead_'+k+'.webp', bg:'art/bg_castle.webp'}); });
 L.push({key:'boss', eyebrow:'Boss defeated', title:'I beat a boss in Axes & Aces!', sub:'A dark comic card adventure. Fight monsters with poker hands.', fig:'art/dead_dragon.webp', bg:'art/bg_castle.webp'});
 for(let w=1;w<=10;w++){ loadWorld(w-1); L.push({key:'quest'+w, eyebrow:'Quest complete', title:w===1?'I saved Anna and was knighted Sir Edward!':'I completed '+worldName(w-1)+'!', sub:'A dark comic card adventure. Fight monsters with poker hands.', fig:'art/hero_t4.webp', bg:w===1?'art/sc_end_3.webp':'art/'+BGF(3)+'.webp'}); }
 loadWorld(0);
 L.push({key:'fallen', eyebrow:'My adventure', title:'My best run so far', sub:'A dark comic card adventure. Fight monsters with poker hands.', fig:'art/hero_t2.webp', bg:'art/bg_forest.webp'});
 for(let t=0;t<=5;t++) L.push({key:'fallen_t'+t, eyebrow:'My adventure', title:'My best run so far', sub:'A dark comic card adventure. Fight monsters with poker hands.', fig:'art/hero_t'+t+'.webp', bg:'art/bg_forest.webp'});
 L.push({key:'level', eyebrow:'Level up', title:'I leveled up in Axes & Aces!', sub:'Every level makes every attack hit harder.', fig:'art/hero_t3.webp', bg:'art/bg_cellar.webp'});
 for(let t=0;t<=5;t++) L.push({key:'level_t'+t, eyebrow:'Level up', title:'I leveled up in Axes & Aces!', sub:'Every level makes every attack hit harder.', fig:'art/hero_t'+t+'.webp', bg:'art/bg_cellar.webp'});
 L.push({key:'daily', eyebrow:'Daily Challenge', title:'Beat my Daily Challenge score!', sub:'Same monsters and same cards for everyone today.', fig:'art/hero_t3.webp', bg:'art/bg_castle.webp'});
 L.push({key:'game', eyebrow:'Free dark comic card adventure', title:'Fight monsters with poker hands', sub:'Save Anna, become Sir Edward, conquer 10 quests and the Endless Abyss.', fig:'art/dragon.webp', bg:'art/bg_castle.webp'});
 return L;})()`));
fs.mkdirSync('site/b',{recursive:true});
for(const o of list){ const u=await p.evaluate(async o=>{const c=await window.__A.ev("bragCard")(o);return c.toDataURL('image/jpeg',.88)},o); fs.writeFileSync('site/b/'+o.key+'.jpg',Buffer.from(u.split(',')[1],'base64')); }
fs.writeFileSync('/tmp/claude-0/og.json',JSON.stringify(list));console.log(list.length,errs);await b.close();})();