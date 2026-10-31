p='game.html'; s=open(p).read()
def rep(a,b):
    global s
    assert a in s, 'MISSING: '+a[:90]; s=s.replace(a,b,1)

# 1) bigger hits for bigger hands: size of number, shake strength, a tiny freeze, deeper boom
rep("function hitFoe(dmg){","function hitFoe(dmg, tier=0){")
rep("""  anim($('foeIcon'),'hit'); thud();
  pop($('foeIcon'), `-${fmt(dmg-absorbed)}`, 'dmg'); if(absorbed) pop($('foeBlock'),`${absorbed} blocked`,'b');
  if(dmg-absorbed >= f.max*.3) shake();""","""  anim($('foeIcon'),'hit'); thud(); if(tier>=2) bigBoom(tier);
  pop($('foeIcon'), `-${fmt(dmg-absorbed)}`, 'dmg t'+tier); if(absorbed) pop($('foeBlock'),`${absorbed} blocked`,'b');
  if(tier>=2) shake(tier); else if(dmg-absorbed >= f.max*.3) shake();""")
rep("function shake(){ if(reduced()) return; const a=$('app'); a.classList.remove('shake'); void a.offsetWidth; a.classList.add('shake'); }",
    "function shake(t=1){ if(reduced()) return; const a=$('app'); a.classList.remove('shake','shake2','shake3'); void a.offsetWidth; a.classList.add(t>=4?'shake3':t>=2?'shake2':'shake'); }\nfunction bigBoom(t){ if(!soundOn||!ac) return; blip(55,.5+t*.1,'sine',.18); blip(42,.7,'sawtooth',.06,.03); if(t>=3) blip(30,.9,'sine',.14,.06); }")
rep("  hitFoe(dmg);\n","  const tier={high:0,pair:0,two:1,trio:1,straight:2,flush:2,full:3,four:4,sflush:5}[ev.type]||0;\n  if(tier>=3&&!reduced()){ document.body.classList.add('hitstop'); await wait(140+tier*30); document.body.classList.remove('hitstop'); }\n  hitFoe(dmg, tier);\n")

# 2) records: new best hit, fastest boss
rep("  achOnHand(ev, played, dmg); if(S.daily) S.daily.atks++;","  const prevBest=life().best; achOnHand(ev, played, dmg); if(S.daily) S.daily.atks++;\n  if(prevBest>0 && dmg>prevBest) setTimeout(()=>ribbon('New best hit!', fmt(dmg)), 900);")

# 3) flawless / clutch + record boss kill, measured at the win
rep("  achOnWin(d);","""  const fl=S.fight||{}, flawless=fl.hp0!=null&&S.hp>=fl.hp0, clutch=!flawless&&S.hp<S.maxHp*.15;
  let bonus=0; if(flawless){ bonus=gold; S.gold+=bonus; }
  if(d.boss){ const L=life(), k='boss_'+d.name, at=fl.atks||0, rec=(L.fast||{})[k]; if(at && (!rec||at<rec)){ lifeAdd(X=>{ X.fast=X.fast||{}; X.fast[k]=at; }); if(rec) setTimeout(()=>ribbon('Fastest boss kill!', at+' attacks'),1400); } }
  S.winMood={flawless, clutch, bonus};
  achOnWin(d);""")

# victory screen: count-up rewards + stamps
rep("""      <div class="rw xp" style="--d:.15s"><span class="ri">${I('xp')}</span><b>+${w.xp}</b>""","""      <div class="rw xp" style="--d:.15s"><span class="ri">${I('xp')}</span><b class="count" data-to="${w.xp}" data-pre="+">+0</b>""")
rep("""      <div class="rw gd" style="--d:.3s"><span class="ri">${I('coin')}</span><b>+${w.gold}</b>""","""      <div class="rw gd" style="--d:.3s"><span class="ri">${I('coin')}</span><b class="count coin-count" data-to="${w.gold+((S.winMood&&S.winMood.bonus)||0)}" data-pre="+">+0</b>""")
rep("""  if(w.drop&&w.drop.kind==='drink'&&w.drop.pending)""","""  countUp(); const mood=S.winMood; S.winMood=null;
  if(mood&&mood.flawless) setTimeout(()=>stamp('FLAWLESS', mood.bonus?`Double gold +${mood.bonus}`:'Not a scratch'), 500);
  else if(mood&&mood.clutch) setTimeout(()=>stamp('CLUTCH!', 'Won by a hair','clutch'), 500);
  if(w.drop&&w.drop.kind==='drink'&&w.drop.pending)""")

JS=r'''
/* ---- round 1 juice: counting rewards, stamps, record ribbons ---- */
function countUp(){
  document.querySelectorAll('#panel .count').forEach((el,k)=>{ const to=+el.dataset.to||0, pre=el.dataset.pre||'', coin=el.classList.contains('coin-count');
    const dur=Math.min(1600, 500+to*20), t0=performance.now()+450+k*150; let last=-1;
    const tick=now=>{ if(!el.isConnected) return; const q=Math.max(0,Math.min(1,(now-t0)/dur)), v=Math.round(to*(1-Math.pow(1-q,3)));
      if(v!==last){ el.textContent=pre+fmt(v); if(coin&&v>last&&last>=0&&soundOn&&ac) blip(1500+Math.random()*700,.05,'triangle',.03); last=v; }
      if(q<1) requestAnimationFrame(tick); else { el.classList.add('done'); if(coin) coins(); } };
    requestAnimationFrame(tick); });
}
function stamp(t, sub, cls=''){
  const e=document.createElement('div'); e.className='stamp '+cls; e.innerHTML=`<b>${t}</b><small>${sub}</small>`;
  document.body.appendChild(e); thud(); if(cls!=='clutch') trumpetCall(); else { brass(196,0,.5,.05); brass(261.63,.25,.9,.05); }
  setTimeout(()=>e.classList.add('out'),2000); setTimeout(()=>e.remove(),2500);
}
function ribbon(t, v){
  const e=document.createElement('div'); e.className='ribbon-rec'; e.innerHTML=`<small>${t}</small><b>${v}</b>`;
  document.body.appendChild(e); blip(1320,.12,'triangle',.05); blip(1760,.18,'triangle',.05,.1); setTimeout(()=>e.classList.add('out'),2600); setTimeout(()=>e.remove(),3100);
}
'''
rep("/* ---- once-in-a-while hands get a huge, screenshot-worthy moment ---- */", JS+"/* ---- once-in-a-while hands get a huge, screenshot-worthy moment ---- */")

CSS='''
/* round 1: bigger hits, stamps, ribbons */
.pop.dmg.t1{font-size:clamp(2.6rem,11vw,4rem)}
.pop.dmg.t2{font-size:clamp(3rem,13vw,4.8rem);background:#d0281c;box-shadow:0 0 22px rgba(255,120,40,.8),0 4px 0 #000}
.pop.dmg.t3,.pop.dmg.t4,.pop.dmg.t5{font-size:clamp(3.6rem,16vw,6rem);background:linear-gradient(#ffcf3d,#e2342a);color:#fff;-webkit-text-stroke:2px #000;box-shadow:0 0 34px rgba(255,190,60,.95),0 5px 0 #000;animation:riseBig 1.3s ease-out forwards}
@keyframes riseBig{0%{transform:translate(-50%,-50%) scale(2.2);opacity:0}15%{transform:translate(-50%,-50%) scale(1);opacity:1}100%{transform:translate(-50%,-160%) scale(1.05);opacity:0}}
#app.shake2{animation:shake2 .5s}
#app.shake3{animation:shake3 .7s}
@keyframes shake2{15%{transform:translate(-14px,5px)}30%{transform:translate(12px,-6px)}45%{transform:translate(-9px,3px)}60%{transform:translate(7px,-2px)}80%{transform:translate(-3px,1px)}}
@keyframes shake3{10%{transform:translate(-22px,8px) rotate(-.6deg)}25%{transform:translate(20px,-10px) rotate(.5deg)}40%{transform:translate(-15px,6px)}55%{transform:translate(11px,-4px)}70%{transform:translate(-6px,2px)}85%{transform:translate(3px,-1px)}}
body.hitstop #app{filter:brightness(1.6) contrast(1.2) saturate(1.3)}
.count.done{animation:countPop .35s cubic-bezier(.2,1.6,.4,1)}
@keyframes countPop{50%{transform:scale(1.35)}}
.stamp{position:fixed;left:50%;top:38%;z-index:115;transform:translate(-50%,-50%) rotate(-10deg);pointer-events:none;text-align:center;
  border:8px solid #3fae4a;border-radius:16px;padding:6px 26px;background:rgba(10,20,10,.75);box-shadow:0 0 0 4px #000,0 0 40px rgba(63,174,74,.7);animation:stampIn .45s cubic-bezier(.3,1.6,.5,1) both}
.stamp b{display:block;font-family:var(--f-title);font-weight:400;font-size:clamp(3rem,14vw,6rem);line-height:1;color:#7be38a;text-shadow:4px 4px 0 #000}
.stamp small{display:block;font-family:var(--f-num);font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#fff;font-size:1rem}
.stamp.clutch{border-color:#e2342a;box-shadow:0 0 0 4px #000,0 0 40px rgba(226,52,42,.8);background:rgba(30,5,5,.78)}.stamp.clutch b{color:#ff8b7e}
.stamp.out{opacity:0;transition:opacity .45s}
@keyframes stampIn{0%{transform:translate(-50%,-50%) rotate(-10deg) scale(3);opacity:0}100%{transform:translate(-50%,-50%) rotate(-10deg) scale(1);opacity:1}}
.ribbon-rec{position:fixed;right:max(16px,env(safe-area-inset-right,0px));top:calc(70px + env(safe-area-inset-top,0px));z-index:116;pointer-events:none;background:linear-gradient(#ffd35c,#d89a14);color:#16100d;border:3px solid #000;border-radius:10px;box-shadow:4px 4px 0 #000,0 0 22px rgba(255,210,90,.7);padding:6px 16px;text-align:center;animation:ribIn .5s cubic-bezier(.2,1.5,.4,1) both}
.ribbon-rec small{display:block;font-family:var(--f-num);font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:.75rem}
.ribbon-rec b{display:block;font-family:var(--f-title);font-weight:400;font-size:1.8rem;line-height:1.05}
.ribbon-rec.out{opacity:0;transform:translateX(30px);transition:all .45s}
@keyframes ribIn{0%{transform:translateX(120%)}100%{transform:none}}
@media (prefers-reduced-motion:reduce){.stamp,.ribbon-rec,.pop.dmg{animation-duration:.01s!important}}
'''
i=s.rindex('</style>'); s=s[:i]+CSS+s[i:]
open(p,'w').write(s); print('ok')
