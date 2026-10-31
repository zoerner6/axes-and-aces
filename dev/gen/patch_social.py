p='game.html'; s=open(p).read()
def rep(a,b):
    global s
    assert a in s, 'MISSING: '+a[:80]; s=s.replace(a,b,1)

JS = r'''
/* ================= recorded music: a song per world, a boss song, smooth crossfades ================= */
const SONG_BAD = new Set();
let musBus=null, song=null;
function songWant(){
  if(!musicOn || !S) return null;
  const fightish = S.phase==='play'||S.phase==='intro';
  let boss=false; try{ boss = fightish && !S.huntFoe && foeDef() && foeDef().boss; }catch(e){}
  return boss ? 'boss' : 'w'+(((S.world||0)%10)+1);
}
function songStart(id){
  if(!musBus){ musBus=ac.createGain(); musBus.gain.value=.55; musBus.connect(ac.destination); }
  const a=new Audio(`music/${id}.mp3`); a.preload='auto';
  let node; try{ node=ac.createMediaElementSource(a); }catch(e){ SONG_BAD.add(id); return null; }
  const g=ac.createGain(); g.gain.value=0; node.connect(g); g.connect(musBus);
  const me={id,a,g,next:false};
  a.addEventListener('error',()=>{ SONG_BAD.add(id); if(song===me){ song=null; updateMusic(); } });
  a.addEventListener('timeupdate',()=>{ if(song===me && !me.next && a.duration && a.currentTime>a.duration-4){ me.next=true; songSwap(id); } });
  a.play().then(()=>{ g.gain.setTargetAtTime(1,ac.currentTime,.7); }).catch(()=>{});
  return me;
}
function songStop(me){ if(!me) return; try{ me.g.gain.setTargetAtTime(0,ac.currentTime,.6); }catch(e){} setTimeout(()=>{ try{ me.a.pause(); me.g.disconnect(); }catch(e){} },3500); }
function songSwap(id){ const old=song; song=songStart(id); songStop(old); }
'''

JS2 = r'''
/* ================= travelers and finds appear where Edward actually is ================= */
const FIND_FIG = {chest:'p_chest', fallen:'p_fallen', trap:'p_trap', mushroom:'p_mushroom', hermit:'p_hermit', villager:'p_villager', farmer:'p_villager', minstrel:'p_minstrel', knight:'p_knight'};

/* ================= achievements, lifetime stats, brag cards, daily challenge ================= */
const SITE='https://zoerner6.github.io/axes-and-aces/';
const ACH=[
 {id:'first_win', name:'First Blood', desc:'Win your first fight', icon:'sword'},
 {id:'one_shot', name:'One and Done', desc:'Defeat a monster with a single attack', icon:'attack'},
 {id:'flawless', name:'Untouched', desc:'Win a fight without losing any health', icon:'shield'},
 {id:'comeback', name:'By a Thread', desc:'Win a fight with less than 10% health left', icon:'heart'},
 {id:'straight', name:'Straight Shooter', desc:'Attack with a Straight', icon:'attack'},
 {id:'flush', name:'Flush of Power', desc:'Attack with a Flush', icon:'attack'},
 {id:'full', name:'Full House Party', desc:'Attack with a Full House', icon:'attack'},
 {id:'four', name:'Four Horsemen', desc:'Attack with Four of a Kind', icon:'attack'},
 {id:'sflush', name:'Straight Flush!', desc:'Attack with a Straight Flush', icon:'attack'},
 {id:'royal', name:'Royal Flush', desc:'Attack with 10, J, Q, K, A of one suit', icon:'level'},
 {id:'hit1k', name:'Heavy Hitter', desc:'Deal 1,000 damage in one attack', icon:'axe'},
 {id:'hit10k', name:'Giant Slayer', desc:'Deal 10,000 damage in one attack', icon:'axe'},
 {id:'hit100k', name:'Earthshaker', desc:'Deal 100,000 damage in one attack', icon:'axe'},
 {id:'boss1', name:'Boss Breaker', desc:'Defeat your first boss', icon:'skull'},
 {id:'bosses10', name:'Boss Hunter', desc:'Defeat 10 bosses', icon:'skull'},
 {id:'rescue', name:'Sir Edward', desc:'Rescue Anna and be knighted by the King', icon:'level'},
 {id:'quests5', name:'Halfway Hero', desc:'Complete 5 quests', icon:'map'},
 {id:'quests10', name:'Legend of the Realm', desc:'Complete all 10 quests', icon:'map'},
 {id:'endless3', name:'Into the Endless', desc:'Reach Endless Depth 3', icon:'map'},
 {id:'lvl10', name:'Veteran', desc:'Reach level 10', icon:'xp'},
 {id:'lvl25', name:'Champion', desc:'Reach level 25', icon:'xp'},
 {id:'rich', name:'Pockets Full', desc:'Hold 100 gold at once', icon:'coin'},
 {id:'potions10', name:'Potion Fan', desc:'Drink 10 potions', icon:'potion'},
 {id:'daily', name:'Daily Duelist', desc:'Finish a Daily Challenge', icon:'chest'},
 {id:'daily5', name:'Daily Champion', desc:'Win all 5 fights of a Daily Challenge', icon:'chest'}
];
const life = ()=>Object.assign({wins:0,bosses:0,hands:0,best:0,bestName:'',gold:0,potions:0,quests:0,deaths:0,level:1,dailyBest:0}, store.get('aa_life',{}));
function lifeAdd(fn){ const L=life(); fn(L); store.set('aa_life',L); }
const achHave = ()=>store.get('aa_ach',{});
function unlock(id){
  if(S&&S.daily&&!['daily','daily5','straight','flush','full','four','sflush','royal','hit1k','hit10k','hit100k','one_shot','flawless','comeback'].includes(id)) return;
  const have=achHave(); if(have[id]) return; have[id]=Date.now(); store.set('aa_ach',have);
  const a=ACH.find(x=>x.id===id); if(!a) return;
  const e=document.createElement('div'); e.className='ach-pop';
  e.innerHTML=`<span class="ach-ic">${I(a.icon)}</span><span><small>Achievement unlocked!</small><b>${a.name}</b><em>${a.desc}</em></span><button data-act="brag" data-kind="ach" data-id="${a.id}">Brag</button>`;
  document.body.appendChild(e); trumpetCall(); setTimeout(()=>e.classList.add('out'),5200); setTimeout(()=>e.remove(),5800);
}
function achOnHand(ev, played, dmg){
  lifeAdd(L=>{ L.hands++; if(dmg>L.best){ L.best=dmg; L.bestName=HANDS[ev.type].name; } });
  if(['straight','flush','full','four','sflush'].includes(ev.type)) unlock(ev.type);
  if(ev.type==='sflush' && ev.cards.some(c=>c.rank===14) && ev.cards.some(c=>c.rank===13)) unlock('royal');
  if(dmg>=1000) unlock('hit1k'); if(dmg>=10000) unlock('hit10k'); if(dmg>=100000) unlock('hit100k');
  if(S.fight) S.fight.atks=(S.fight.atks||0)+1;
}
function achOnWin(d){
  const f=S.fight||{};
  lifeAdd(L=>{ L.wins++; if(d.boss) L.bosses++; L.gold+=d.gold||0; L.level=Math.max(L.level,S.level); });
  unlock('first_win'); if((f.atks||0)===1) unlock('one_shot');
  if(f.hp0!=null && S.hp>=f.hp0) unlock('flawless');
  if(S.hp < S.maxHp*.1) unlock('comeback');
  if(d.boss){ unlock('boss1'); if(life().bosses>=10) unlock('bosses10'); }
  if(S.level>=10) unlock('lvl10'); if(S.level>=25) unlock('lvl25');
  if(S.gold>=100) unlock('rich');
}
function achOnQuest(){
  lifeAdd(L=>{ L.quests=Math.max(L.quests,S.world||0); });
  if((S.world||0)>=1) unlock('rescue'); if(S.world>=5) unlock('quests5'); if(S.world>=10) unlock('quests10'); if(S.world>=12) unlock('endless3');
}

/* ---- brag cards: a 1200x630 picture made for Facebook, linking back to the game ---- */
const imgLoad = src => new Promise(r=>{ const i=new Image(); i.onload=()=>r(i); i.onerror=()=>r(null); i.src=src; });
function wrapText(ctx, t, x, y, w, lh){ const words=t.split(' '); let line='', yy=y; for(const wd of words){ const tt=line?line+' '+wd:wd; if(ctx.measureText(tt).width>w && line){ ctx.fillText(line,x,yy); line=wd; yy+=lh; } else line=tt; } if(line) ctx.fillText(line,x,yy); return yy; }
async function bragCard(o){
  try{ await document.fonts.load('80px "Germania One"'); await document.fonts.load('700 40px Oswald'); }catch(e){}
  const c=document.createElement('canvas'); c.width=1200; c.height=630; const x=c.getContext('2d');
  const bg=await imgLoad(o.bg||'art/bg_tavern.webp');
  if(bg){ const sc=Math.max(1200/bg.width,630/bg.height); x.drawImage(bg,(1200-bg.width*sc)/2,(630-bg.height*sc)/2,bg.width*sc,bg.height*sc); } else { x.fillStyle='#2a1608'; x.fillRect(0,0,1200,630); }
  let gr=x.createLinearGradient(0,0,1200,0); gr.addColorStop(0,'rgba(10,5,3,.94)'); gr.addColorStop(.55,'rgba(10,5,3,.78)'); gr.addColorStop(1,'rgba(10,5,3,.15)'); x.fillStyle=gr; x.fillRect(0,0,1200,630);
  const fig=o.fig?await imgLoad(o.fig):null;
  if(fig){ const h=520, w=fig.width*h/fig.height, fx=Math.min(1180-w, 1200-w*0.92); x.save(); x.shadowColor='rgba(0,0,0,.8)'; x.shadowBlur=30; x.drawImage(fig, fx, 630-h-20, w, h); x.restore(); }
  x.fillStyle='#000'; x.fillRect(0,0,1200,12); x.fillRect(0,618,1200,12);
  x.textBaseline='alphabetic';
  x.font='44px "Germania One", Georgia, serif'; x.fillStyle='#f2b632'; x.fillText('Axes & Aces', 56, 92);
  x.font='700 22px Oswald, Arial'; x.fillStyle='#e8d9bb'; x.fillText((o.eyebrow||'').toUpperCase(), 58, 132);
  x.font='86px "Germania One", Georgia, serif'; x.lineWidth=10; x.strokeStyle='#000'; x.fillStyle='#fff3d0';
  const lines=[]; { const words=o.title.split(' '); let l=''; for(const w of words){ const t=l?l+' '+w:w; if(x.measureText(t).width>700&&l){ lines.push(l); l=w; } else l=t; } lines.push(l); }
  let y=230; for(const l of lines.slice(0,2)){ x.strokeText(l,56,y); x.fillText(l,56,y); y+=92; }
  if(o.big){ x.font='700 96px Oswald, Arial'; x.fillStyle=o.bigColor||'#f2b632'; x.strokeText(o.big,56,y+40); x.fillText(o.big,56,y+40); y+=70; }
  x.font='500 30px "Alegreya Sans", Arial'; x.fillStyle='#e8d9bb'; y=wrapText(x, o.sub||'', 58, y+60, 640, 38);
  x.fillStyle='#f2b632'; x.fillRect(56,532,560,58); x.strokeStyle='#000'; x.lineWidth=4; x.strokeRect(56,532,560,58);
  x.font='700 28px Oswald, Arial'; x.fillStyle='#16100d'; x.fillText('PLAY FREE  ▸  zoerner6.github.io/axes-and-aces', 74, 571);
  return c;
}
function bragInfo(kind, id){
  const w=S?(S.world||0):0, who=(typeof heroName==='function')?heroName():'Edward';
  if(kind==='ach'){ const a=ACH.find(x=>x.id===id)||ACH[0]; return {key:'ach_'+a.id, eyebrow:'Achievement unlocked', title:a.name, sub:a.desc+'. Think you can do it too?', fig:`art/hero_t${heroTier()}.webp`, bg:`art/${BGF(curArea())}.webp`}; }
  if(kind==='boss'){ const d=S.lastWin||{}; const slug=ART[d.name]; return {key:'boss', eyebrow:`${worldName(w)}`, title:`I defeated ${d.name}!`, big:`Level ${S.level}`, sub:`${who} brought down the ${d.name}. Your turn.`, fig: slug?`art/dead_${slug}.webp`:null, bg:`art/${BGF(curArea())}.webp`}; }
  if(kind==='quest'){ return {key:'quest'+Math.min(10,w), eyebrow:'Quest complete', title:w<=1?'I saved Anna and was knighted Sir Edward!':`I completed ${worldName(w-1)}!`, big:`Level ${S.level}`, sub:'Fight monsters with poker hands. Can you finish the quest?', fig:`art/hero_t${heroTier()}.webp`, bg:'art/sc_end_3.webp'}; }
  if(kind==='death'){ const k=S.killer||{}; return {key:'fallen', eyebrow:`${worldName(w)}`, title:`I reached level ${S.level}`, big:`${fmt(S.stats.best||0)} best hit`, sub:`Before the ${k.name||'monsters'} took me down. Beat my score!`, fig:`art/hero_t${heroTier()}.webp`, bg:`art/${BGF(k.area||0)}.webp`}; }
  if(kind==='level'){ return {key:'level', eyebrow:'Level up', title:`I reached level ${S.level}!`, big:`×${S.level} damage`, sub:'Every attack hits harder. How far can you go?', fig:`art/hero_t${heroTier()}.webp`, bg:`art/${BGF(curArea())}.webp`}; }
  if(kind==='daily'){ const r=S.dailyResult||{}; return {key:'daily', eyebrow:`Daily Challenge · ${r.date||''}`, title:r.wins>=5?'I beat today\'s Daily Challenge!':`I won ${r.wins||0} of 5 daily fights`, big:`${fmt(r.score||0)} points`, sub:'Same monsters and same cards for everyone today. Can you beat my score?', fig:r.fig||`art/hero_t${heroTier()}.webp`, bg:r.bg||'art/bg_castle.webp'}; }
  return {key:'game', eyebrow:'Dark comic card adventure', title:'Axes & Aces', sub:'Fight monsters with poker hands.', fig:'art/hero_t3.webp'};
}
const heroTier = ()=>Math.max(0,...['armor','helm','shield'].map(k=>S.eq&&S.eq[k]?S.eq[k].tier:0));
let bragCanvas=null, bragNow=null;
async function bragPanel(kind, id){
  const info=bragInfo(kind,id); bragNow=info; const prev=S.phase;
  openPanel(`<div class="eyebrow">Share it</div><h2>Brag about it</h2><div class="brag-img" id="bragImg"><span>Making your picture...</span></div>
    <div class="brag-btns">
      <button class="btn big brag-fb" data-act="bragFb">Share on Facebook</button>
      <button class="btn big ghost" data-act="bragShare">Share picture</button>
      <button class="btn big ghost" data-act="bragSave">Save picture</button>
      <button class="btn big ghost" data-act="bragCopy">Copy link</button>
    </div>
    <p class="menu-note">Tip: on Facebook, post the saved picture with the link so friends can tap it and play.</p>
    <button class="btn big" data-act="bragClose">Done</button>`);
  S.bragBack=prev;
  bragCanvas=await bragCard(info);
  const im=$('bragImg'); if(im){ im.innerHTML=''; const u=bragCanvas.toDataURL('image/jpeg',.9); const i=new Image(); i.src=u; i.alt=info.title; im.appendChild(i); }
}
const bragUrl = ()=>SITE+'b/'+(bragNow?bragNow.key:'game')+'.html';
const bragText = ()=>bragNow ? `${bragNow.title} ${bragNow.big?'('+bragNow.big+') ':''}Play Axes & Aces free:` : 'Play Axes & Aces free:';
function bragBlob(){ return new Promise(r=>bragCanvas ? bragCanvas.toBlob(b=>r(b),'image/jpeg',.9) : r(null)); }

/* ---- daily challenge: same monsters and same card shuffles for everyone today ---- */
const realRandom=Math.random;
function seeded(a){ return function(){ a|=0; a=a+0x6D2B79F5|0; let t=Math.imul(a^a>>>15,1|a); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
const todayKey = ()=>{ const d=new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; };
const DAILY_STEPS=[1,5,10,16,8];
function startDaily(){
  stopVoice(); const key=todayKey(), seed=+key.replace(/-/g,'');
  Math.random=seeded(seed);
  canSave=false; newRun(false);
  const w=seed%10; S.world=w; loadWorld(w); S.knighted=w>0;
  const lo=AREA_LV[1][0]; S.level=Math.max(3,lo); S.maxHp=400+100*(S.level-1); S.hp=S.maxHp; S.xp=cumNeed(S.level-1);
  const t=Math.min(5,1+Math.floor(S.level/5)); S.eq={main:{type:'sword',tier:t},off:null,shield:{type:'shield',tier:t},helm:{type:'helm',tier:t},armor:{type:'armor',tier:t}};
  S.spells=['potion','potion','rage']; S.coach=-1; S.tips={shop:1,level:1,boss:1,path:1};
  S.daily={key, n:0, wins:0, atks:0}; S.idx=DAILY_STEPS[0]; S.genFoe=null; S.foePick=null; S.enc=null;
  render(); dailyIntro();
}
function dailyIntro(){
  S.phase='dailyIntro';
  openPanel(`<div class="cine-scene"><img src="art/${BGF(1)}.webp" alt=""><span class="cine-title">Daily Challenge</span></div>
    <h2>${todayKey()}</h2>
    <p>Five fights in <b>${worldName(S.world)}</b>. Everyone gets the same monsters and the same cards today. Win as many as you can, as fast as you can.</p>
    <div class="lines"><div><span>Your level</span><b>${S.level}</b></div><div><span>Best today</span><b>${fmt(store.get('aa_daily_'+todayKey(),0))} points</b></div></div>
    <button class="btn big" data-act="dailyGo">Start</button><button class="btn big ghost" data-act="dailyQuit">Back</button>`);
  $('panel').classList.add('cine');
}
function dailyNextFight(){ S.daily.n++; if(S.daily.n>=DAILY_STEPS.length){ dailyDone(); return; } S.idx=DAILY_STEPS[S.daily.n]; S.genFoe=null; S.foePick=null; S.enc=null; S.fight=null; fightIntro(); }
function dailyDone(){
  const D=S.daily, score=D.wins*1000 + Math.max(0,S.hp) + Math.max(0,30-D.atks)*50;
  const best=Math.max(store.get('aa_daily_'+D.key,0),score); store.set('aa_daily_'+D.key,best);
  lifeAdd(L=>{ L.dailyBest=Math.max(L.dailyBest,score); });
  S.dailyResult={date:D.key, wins:D.wins, score, bg:`art/${BGF(1)}.webp`, fig:`art/hero_t${heroTier()}.webp`};
  unlock('daily'); if(D.wins>=5) unlock('daily5');
  Math.random=realRandom; S.phase='dailyDone';
  openPanel(`<div class="vic"><div class="vic-title">${D.wins>=5?'Champion!':'Challenge over'}</div>
    <div class="vic-sub">Daily Challenge · ${D.key}</div>
    <div class="rewards"><div class="rw gd" style="--d:.1s"><span class="ri">${I('chest')}</span><b>${D.wins}/5</b><small>Fights won</small></div>
      <div class="rw xp" style="--d:.2s"><span class="ri">${I('attack')}</span><b>${D.atks}</b><small>Attacks used</small></div>
      <div class="rw lv" style="--d:.3s"><span class="ri">${I('level')}</span><b>${fmt(score)}</b><small>Points</small><em>Best today ${fmt(best)}</em></div></div>
    <button class="btn big brag-fb" data-act="brag" data-kind="daily">Brag about it</button>
    <button class="btn big vic-btn" data-act="dailyQuit">Back to my adventure</button></div>`);
}
function dailyQuit(){
  Math.random=realRandom; canSave=true; closePanel();
  const sv=loadSave(); if(sv){ start({S:sv.S}); } else { newRun(false); render(); storyPanel(); }
}

/* ---- achievements and stats screen ---- */
function achPanel(){
  const have=achHave(), L=life(), n=ACH.filter(a=>have[a.id]).length;
  openPanel(`<div class="eyebrow">Your legend</div><h2>Achievements ${n} / ${ACH.length}</h2>
    <div class="lines stats-lines"><div><span>Fights won</span><b>${fmt(L.wins)}</b></div><div><span>Bosses defeated</span><b>${fmt(L.bosses)}</b></div>
      <div><span>Biggest hit</span><b>${fmt(L.best)}${L.bestName?' ('+L.bestName+')':''}</b></div><div><span>Hands played</span><b>${fmt(L.hands)}</b></div>
      <div><span>Highest level</span><b>${L.level}</b></div><div><span>Quests completed</span><b>${L.quests}</b></div><div><span>Best daily score</span><b>${fmt(L.dailyBest)}</b></div></div>
    <div class="ach-grid">${ACH.map(a=>`<div class="ach ${have[a.id]?'got':''}"><span class="ach-ic">${have[a.id]?I(a.icon):I('lock')}</span><span><b>${a.name}</b><small>${a.desc}</small></span>${have[a.id]?`<button data-act="brag" data-kind="ach" data-id="${a.id}">Brag</button>`:''}</div>`).join('')}</div>
    <button class="btn big" data-act="close">Back</button>`);
}
'''

CSS = r'''
/* achievements, brag cards, daily challenge */
.ach-pop{position:fixed;left:50%;top:calc(14px + env(safe-area-inset-top,0px));transform:translateX(-50%);z-index:120;display:flex;align-items:center;gap:12px;background:#f3e6c8;color:#16100d;border:3px solid #000;border-radius:12px;box-shadow:5px 5px 0 #000,0 0 30px rgba(242,182,50,.6);padding:10px 12px;max-width:min(92vw,520px);animation:achIn .5s cubic-bezier(.2,1.5,.4,1)}
.ach-pop.out{opacity:0;transform:translate(-50%,-30px);transition:all .5s}
.ach-pop .ach-ic .ico{width:46px;height:46px}
.ach-pop small{display:block;font-family:var(--f-num);font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:#8e1a14}
.ach-pop b{display:block;font-family:var(--f-title);font-weight:400;font-size:1.35rem}
.ach-pop em{font-style:normal;font-size:.9rem}
.ach-pop button,.ach button{flex:0 0 auto;background:#1877f2;color:#fff;border:2px solid #000;border-radius:8px;font-weight:800;padding:6px 12px;box-shadow:2px 2px 0 #000;cursor:pointer}
@keyframes achIn{0%{opacity:0;transform:translate(-50%,-40px) scale(.8)}100%{opacity:1;transform:translate(-50%,0)}}
.ach-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px;width:100%}
.ach{display:flex;align-items:center;gap:10px;background:#120d0b;border:2px solid #000;border-radius:10px;padding:8px;opacity:.55}
.ach.got{opacity:1;background:linear-gradient(#2c1f10,#160f09);box-shadow:inset 0 0 0 1px rgba(242,182,50,.45)}
.ach .ach-ic .ico{width:34px;height:34px}.ach>span:nth-child(2){flex:1;min-width:0}
.ach b{display:block;font-family:var(--f-title);font-weight:400;font-size:1.05rem;color:var(--gold)}.ach small{display:block;color:var(--parch-dim);font-size:.82rem;line-height:1.25}
.stats-lines{width:100%}
.brag-img{width:100%;aspect-ratio:1200/630;background:#000;border:3px solid #000;border-radius:8px;box-shadow:4px 4px 0 #000;display:grid;place-items:center;overflow:hidden;color:var(--parch-dim)}
.brag-img img{width:100%;height:100%;object-fit:cover;display:block}
.brag-btns{display:grid;grid-template-columns:1fr 1fr;gap:8px;width:100%}
.btn.brag-fb{background:#1877f2!important;color:#fff!important}
.find-fig{position:absolute;left:50%;bottom:4%;height:84%;width:auto;max-width:70%;object-fit:contain;transform:translateX(-50%);z-index:1;filter:drop-shadow(0 10px 14px rgba(0,0,0,.75));animation:figIn .7s cubic-bezier(.2,1.3,.4,1) both}
@keyframes figIn{0%{opacity:0;transform:translate(-50%,30px) scale(.9)}100%{opacity:1;transform:translate(-50%,0)}}
.menu-list .btn.daily{background:linear-gradient(#5a3c0c,#2a1b06)!important;color:#ffd35c!important}
'''

i=s.index("/* ---------- start ---------- */\nfunction start"); s=s[:i]+JS+JS2+s[i:]
i=s.rindex('</style>'); s=s[:i]+CSS+s[i:]

# music: recorded songs first, synth fallback
rep("function updateMusic(){\n  if(!ac) return;","""function updateMusic(){
  if(!ac) return;
  const sw=songWant();
  if(sw && !SONG_BAD.has(sw)){ if(musicArea>=0) stopMusic(); if(!song||song.id!==sw) songSwap(sw); return; }
  if(song){ songStop(song); song=null; }""")
rep("function duck(on){ if(musicGain&&ac) musicGain.gain.setTargetAtTime(on?.22:.9, ac.currentTime, .3); }",
    "function duck(on){ if(musicGain&&ac) musicGain.gain.setTargetAtTime(on?.22:.9, ac.currentTime, .3); if(musBus&&ac) musBus.gain.setTargetAtTime(on?.15:.55, ac.currentTime, .3); }")
# better built-in narrator voices
rep("function pickVoice(){ try{ const vs=speechSynthesis.getVoices(); return ",
    "function pickVoice(){ try{ const vs=speechSynthesis.getVoices(); return vs.find(v=>/^en/i.test(v.lang)&&/(natural|neural|online)/i.test(v.name)&&/(ryan|thomas|guy|davis|andrew|brian|christopher|eric|male)/i.test(v.name)) || vs.find(v=>/^en/i.test(v.lang)&&/(natural|neural|online)/i.test(v.name)) || vs.find(v=>/Google UK English Male/i.test(v.name)) || ")
# finds in context
rep("""  openPanel(`${cineHTML('find_'+(f.scene||'chest'), f.title, plain)}""","""  const fk=FIND_FIG[f.scene||'chest']||'p_chest', fhtml=cineHTML('find_'+(f.scene||'chest'), f.title, plain, `<img class="find-fig" src="art/${fk}.webp" alt="">`).replace(`src="${sceneImg('find_'+(f.scene||'chest'))}"`, `src="art/${BGF(curArea())}.webp"`);
  openPanel(`${fhtml}""")
rep("const people=[['hermit','An old hermit'],['farmer','A kind farmer'],['minstrel','A traveling minstrel'],['knight','A wandering knight']]",
    "const people=[['hermit','An old hermit'],['villager','A frightened villager'],['minstrel','A traveling minstrel'],['knight','A wandering knight']]")
open(p,'w').write(s)
print('ok')
