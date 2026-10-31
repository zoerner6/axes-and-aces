import sys,re
p=sys.argv[1]; s=open(p).read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt, (s.count(a), a[:100])
    s=s.replace(a,b)
I=lambda n: f'<img class="ico" src="art/i_{n}.webp" alt="">'
# fonts
R('family=Fredoka:wght@500;600;700','family=Fredoka:wght@500;600;700&family=Oswald:wght@500;600;700')
# ---- hero HP bar: no "You", compact, HP label on the roomier side
R('''    <div class="me-name">You <small id="lvlLabel">Level 1</small></div>
    <div class="me-stats"><span class="chip blk" id="myBlock" hidden></span><span class="chip gold" id="goldNum" hidden>$3</span></div>
    <div class="hpbar mehp" style="grid-column:1/-1"><i id="myBar"></i><span id="myHp">40 / 40</span></div>''',
'''    <span id="lvlLabel" hidden></span><span class="chip gold" id="goldNum" hidden></span>
    <div class="hpbar mehp" id="myHpBar"><i id="myBar"></i><span id="myHp">HP 400 / 400</span></div>
    <span class="chip blk" id="myBlock" hidden></span>''')
R("$('myBar').style.width = Math.max(0,S.hp/S.maxHp*100)+'%'; $('myHp').textContent = `${Math.max(0,S.hp)} / ${S.maxHp}`;","hpLabel();")
R("function setMyBars(){ $('myBar').style.width=Math.max(0,S.hp/S.maxHp*100)+'%'; $('myHp').textContent=`${Math.max(0,S.hp)} / ${S.maxHp}`;","function setMyBars(){ hpLabel();")
R("function setFoeBars(){","function hpLabel(){ const pc=Math.max(0,S.hp/S.maxHp*100); $('myBar').style.width=pc+'%'; $('myHp').textContent=`HP ${Math.max(0,S.hp)} / ${S.maxHp}`; $('myHpBar').classList.toggle('lo',pc<50); }\nfunction setFoeBars(){")
# ---- icons in data
R("const SPELLS = [", f"const I = n => `<img class=\"ico\" src=\"art/i_${{n}}.webp\" alt=\"\" draggable=\"false\">`;\nconst SPELLS = [")
for a,b in [("icon:'🧪', price:4, desc:'Heal","icon:I('potion'), price:4, desc:'Heal"),("icon:'🪨'","icon:I('ironskin')"),("icon:'💢'","icon:I('rage')"),
            ("icon:'⚔️', mat:'w', hands:1","icon:I('sword'), mat:'w', hands:1"),("icon:'🪓', mat:'w', hands:2","icon:I('axe'), mat:'w', hands:2"),
            ("name:'Dagger',     icon:'🗡️'","name:'Dagger',     icon:I('dagger')"),("name:'Shield',     icon:'🛡️'","name:'Shield',     icon:I('shield')"),
            ("icon:'⛑️'","icon:I('helm')"),("icon:'🦺'","icon:I('armor')"),
            ("name:'Fire Bolt',          icon:'🔥'","name:'Fire Bolt',          icon:I('fire')"),("icon:'❄️', school","icon:I('frost'), school"),("icon:'⚡', school","icon:I('bolt'), school")]:
    R(a,b)
R("icon:'💚', school:'cleric'","icon:I('cleric'), school:'cleric'",3)
R("const bag = n => `<span class=\"bag\"><span class=\"bi\">💰</span><b>${n}</b></span>`;","const bag = n => `<span class=\"bag\">${I('coin')}<b>${n}</b></span>`;")
R("const coin = n => `<span class=\"coin\">${n}</span>`;","const coin = n => `<span class=\"coinv\">${I('coin')}${n}</span>`;")
R('''data-k="h" data-i="x" aria-label="Healing round">💚</button>''','''data-k="h" data-i="x" aria-label="Healing round">${I('cleric')}</button>''')
R('''`<div class="slot empty locked">🔒</div>`''','''`<div class="slot empty locked">${I('lock')}</div>`''',2)
R("({main:'⚔️',off:'🗡️',shield:'🛡️',helm:'⛑️',armor:'🦺'})[k]","({main:I('sword'),off:I('dagger'),shield:I('shield'),helm:I('helm'),armor:I('armor')})[k]")
# satchel ribbon + pills
R('''<span class="lv">🎖️ Lv <b id="lvlNum">1</b></span>''','''<span class="lv"><img class="ico" src="art/i_level.webp" alt=""> Lv <b id="lvlNum">1</b></span>''')
R('''<span class="gold">💰 <b id="goldNum2">3</b></span>''','''<span class="gold"><img class="ico" src="art/i_coin.webp" alt=""><b id="goldNum2">3</b></span>''')
R('''<span class="a">⚔ <b id="atkNum">+0</b></span><span class="d">🛡 <b id="defNum">+0</b></span>''','''<span class="a"><img class="ico" src="art/i_attack.webp" alt="Attack"><b id="atkNum">+0</b></span><span class="d"><img class="ico" src="art/i_defense.webp" alt="Defense"><b id="defNum">+0</b></span>''')
R("$('xpNum').textContent=`⭐ ${S.xp} / ${hi} EXP`;","$('xpNum').textContent=`EXP ${S.xp} / ${hi}`;")
R('''<div class="totB"><span class="a">⚔ Attack +${weaponPts()}</span><span class="d">🛡 Defense +${defense()}</span></div>''','''<div class="totB"><span class="a">${I('attack')} Attack +${weaponPts()}</span><span class="d">${I('defense')} Defense +${defense()}</span></div>''')
# fight intro: show gold
R('''<div class="fc-stats"><span>🎖️ Lv <em>${d.lvl||'?'}</em></span><span>❤️ <em>${fmt(d.hp)}</em> HP</span><span>⭐ <em>${d.xp||'?'}</em> EXP</span>''',
  '''<div class="fc-stats"><span>${I('level')} Lv <em>${d.lvl||'?'}</em></span><span>${I('heart')} <em>${fmt(d.hp)}</em> HP</span><span>${I('xp')} <em>${d.xp||'?'}</em> EXP</span><span>${I('coin')} <em>${d.gold+gearHas('earn')}</em> Gold</span>''')
# victory
R('''<span class="ri">⭐</span><b>+${w.xp}</b>''','''<span class="ri">${I('xp')}</span><b>+${w.xp}</b>''')
R('''<span class="ri">💰</span><b>+${coin(w.gold)}</b><small>Gold</small><em>Total 💰 ${S.gold}</em>''','''<span class="ri">${I('coin')}</span><b>+${w.gold}</b><small>Gold</small><em>Total ${S.gold}</em>''')
R('''<span class="ri">🎖️</span><b>${S.level}</b>''','''<span class="ri">${I('level')}</span><b>${S.level}</b>''')
# shop
R('''<span class="inn-ic">🛏️<i>✚</i></span>''','''<span class="inn-ic">${I('inn')}<i>✚</i></span>''')
R('''<span>⚒️ Blacksmith</span>''','''<span>${I('sword')} Blacksmith</span>''')
R('''<span>📚 Spellbooks</span>''','''<span>${I('fire')} Spellbooks</span>''')
R('''<span>🧪 Potions</span></div>''','''<span>${I('potion')} Potions</span></div>''')
R('''    <div class="row"><button class="btn big" data-act="leaveShop">Onward!</button></div></div></div>`);''','''    </div></div>`);''')
i=s.index('''    ${tip('shop',''')
s=s[:i]+'''    <div class="row"><button class="btn big" data-act="leaveShop">Onward!</button></div>
'''+s[i:]
# finds
R("f={icon:'🧰'","f={icon:I('chest')",2)
R("f={icon:'🦴'","f={icon:I('skull')",2)
R("f={icon:'🪤'","f={icon:I('trap')")
R("f={icon:'🍄'","f={icon:I('mushroom')")
R("'🧳 Traveling Merchant'","'Traveling Merchant'",0) if "'🧳 Traveling Merchant'" in s else None
R('<h2>🧳 Traveling Merchant</h2>','<h2>Traveling Merchant</h2>')
# ---- monster attack: lunge and claw slashes
R('''    anim($('foeIcon'),'lunge');
    await wait(220);''','''    anim($('foeIcon'),'lunge'); swoosh();
    await wait(300); claws();''')
R("function hitFoe(dmg){",'''function claws(){
  if(reduced()) return;
  const r=$('heroBox').getBoundingClientRect(), cx=r.left+r.width/2, cy=r.top+r.height/2;
  const fl=document.createElement('div'); fl.className='redflash'; $('fx').appendChild(fl); setTimeout(()=>fl.remove(),450);
  [-1,0,1].forEach((k,i)=>{ const c=document.createElement('div'); c.className='claw';
    c.style.left=(cx+k*34)+'px'; c.style.top=(cy-60+k*10)+'px'; c.style.animationDelay=(i*45)+'ms'; $('fx').appendChild(c); setTimeout(()=>c.remove(),700); });
}
function hitFoe(dmg){''')
# ---- narrator (recorded files when present, else the browser's own voice)
R("let soundOn = store.get('sound', true), musicOn = store.get('music', true), fast = false;",
  "let soundOn = store.get('sound', true), musicOn = store.get('music', true), voiceOn = store.get('voice', true), fast = false;")
R('''          <button class="sndtog" data-act="togSfx" id="togSfx"><span>🔊 Sound effects</span><i></i></button>''','''          <button class="sndtog" data-act="togSfx" id="togSfx"><span>🔊 Sound effects</span><i></i></button>
          <button class="sndtog" data-act="togVoice" id="togVoice"><span>🗣️ Narrator</span><i></i></button>''')
R("$('togSfx').classList.toggle('on',soundOn);","$('togSfx').classList.toggle('on',soundOn); $('togVoice').classList.toggle('on',voiceOn);")
R("    case 'togSfx':","    case 'togVoice': voiceOn=!voiceOn; store.set('voice',voiceOn); if(!voiceOn) stopVoice(); render(); break;\n    case 'capDone': finishCaption(); break;\n    case 'playVo': if(cineNow) { voiceOn=true; store.set('voice',true); render(); cineNow(); } break;\n    case 'togSfx':")
R("/* ---------- state ---------- */",'''/* ---------- narrator + animated scenes ---------- */
const VO = [];  /* recorded narration files (art/vo_<key>_<page>.mp3); others use the browser's voice */
let vo=null, typeTimer=0, typeDelay=0, cineNow=null;
function duck(on){ if(musicGain&&ac) musicGain.gain.setTargetAtTime(on?.22:.9, ac.currentTime, .3); }
function pickVoice(){ try{ const vs=speechSynthesis.getVoices(); return vs.find(v=>/en-GB/i.test(v.lang)&&/(daniel|george|arthur|ryan|male)/i.test(v.name)) || vs.find(v=>/en-GB/i.test(v.lang)) || vs.find(v=>/^en/i.test(v.lang)); }catch(e){ return null; } }
function stopVoice(){ if(vo&&vo.pause) vo.pause(); try{ speechSynthesis.cancel(); }catch(e){} vo=null; duck(false); }
/* speaks text; calls onTime(seconds) with how long it should take so captions can keep pace */
function narrate(text, id, onTime){
  stopVoice(); if(!voiceOn) return false; audio();
  if(id && VO.includes(id)){ const a=new Audio(`art/${id}.mp3`); vo=a;
    a.addEventListener('loadedmetadata',()=>{ if(vo===a&&isFinite(a.duration)) onTime&&onTime(a.duration); });
    a.addEventListener('ended',()=>{ if(vo===a){ vo=null; duck(false); } });
    a.play().then(()=>duck(true)).catch(()=>{ const b=document.querySelector('.cine-voice'); if(b) b.hidden=false; }); return true; }
  if(!('speechSynthesis' in window)) return false;
  try{ const u=new SpeechSynthesisUtterance(text.replace(/<[^>]+>/g,'')), v=pickVoice(); if(v) u.voice=v; u.rate=.94; u.pitch=.82;
    u.onend=()=>{ if(vo===u){ vo=null; duck(false); } }; vo=u; duck(true); speechSynthesis.speak(u); onTime&&onTime(text.length/13.5); return true; }catch(e){ return false; }
}
function typeCaption(text, secs, delay=0){
  const el=$('capTxt'); if(!el) return; clearInterval(typeTimer); clearTimeout(typeDelay);
  el.textContent=''; el.dataset.full=text; let n=0; const step=Math.max(12, secs*1000/Math.max(1,text.length));
  typeDelay=setTimeout(()=>{ typeTimer=setInterval(()=>{ n++; el.textContent=text.slice(0,n); if(n>=text.length) clearInterval(typeTimer); }, step); }, delay);
}
function finishCaption(){ const el=$('capTxt'); if(!el) return; clearInterval(typeTimer); clearTimeout(typeDelay); el.textContent=el.dataset.full||''; }
const sceneImg = id => `art/sc_${id}.webp`;
function cineHTML(id, title, text, extra=''){
  const kb=['kb1','kb2','kb3'][id.length%3];
  return `<div class="cine-scene ${kb}"><img src="${sceneImg(id)}" alt="">${extra}<span class="cine-title">${title}</span>
    <button class="cine-voice" data-act="playVo" hidden>🔈 Hear the narrator</button></div>
    <div class="cine-cap" data-act="capDone"><p><span class="ghost">${text}</span><span class="typed" id="capTxt"></span></p></div>`;
}
function runCine(id, title, text){
  const start=()=>{ const spoke=narrate(title+'. '+text, 'vo_'+id, secs=>{ const tPart=(title.length+2)/(title.length+2+text.length); typeCaption(text, secs*(1-tPart)*.95, secs*tPart*1000); });
    if(!spoke) typeCaption(text, text.length/26); };
  cineNow=start; start();
}

/* ---------- state ---------- */''')
# story panels become animated scenes
i=s.index('function storyPanel(){'); j=s.index('function storyNext(){')
s=s[:i]+'''function storyPanel(){
  const pages=STORIES[S.story.key], pg=pages[S.story.page], last=S.story.page===pages.length-1;
  const btn = !last ? 'Next' : S.story.key==='end' ? 'The end' : 'Ready';
  const id=`${S.story.key}_${S.story.page}`, plain=pg.text.replace(/<[^>]+>/g,'');
  const embers = S.story.key==='start'||(S.story.key==='end'&&S.story.page===2) ? `<span class="embers">${Array.from({length:10},(_,k)=>`<i style="left:${8+k*9}%;animation-delay:${(k*.7)%4}s;animation-duration:${4+k%3}s"></i>`).join('')}</span>` : '';
  openPanel(`${cineHTML(id, pg.title, plain, embers)}
    <div class="cine-foot">${pages.length>1?`<div class="dots">${pages.map((_,i)=>`<i class="${i===S.story.page?'on':''}"></i>`).join('')}</div>`:'<span></span>'}
    <button class="btn big" data-act="storyNext">${btn}</button></div>`);
  $('panel').classList.add('cine');
  runCine(id, pg.title, plain);
}
'''+s[j:]
R("function openPanel(html){ $('bubble').hidden=true; $('panel').classList.remove('wide','parch');","function openPanel(html){ stopVoice(); clearInterval(typeTimer); clearTimeout(typeDelay); cineNow=null; $('bubble').hidden=true; $('panel').classList.remove('wide','parch','cine');")
R("function closePanel(){ $('overlay').hidden=true;","function closePanel(){ stopVoice(); $('overlay').hidden=true;")
# trade becomes an animated merchant scene
R('''  openPanel(`<div class="eyebrow">Traveling Merchant</div><h2>A deal is struck</h2>
    <div class="trade">''','''  const said=[`Ah, the ${nm}! A fine choice. That will be ${t.price} gold.`, ...t.trades.map(x=>`I'll buy your old ${x.name} for ${x.pay} gold.`), `${e.atk?'Swing it well':'May it keep you safe'}, hero!`].join(' ');
  openPanel(`<div class="cine-scene kb2 short"><img src="${sceneImg('merchant')}" alt=""><span class="cine-title">A deal is struck</span></div>
    <div class="trade">''')
R('''  lines.forEach((l,i)=>setTimeout(()=>{ if(S.phase!=='trade') return;''','''  $('panel').classList.add('cine'); narrate(said);
  lines.forEach((l,i)=>setTimeout(()=>{ if(S.phase!=='trade') return;''')
open(p,'w').write(s); print('ok')
