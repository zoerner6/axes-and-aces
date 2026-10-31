p='game.html'; s=open(p).read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:90]); s=s.replace(a,b)
# Rose -> Brianna
s=s.replace("Rosie's","Bri's").replace("my Rosie","my Brianna").replace("Rose","Brianna")
# narrator off by default (the browser voice sounds robotic)
R("voiceOn = store.get('voice', true)","voiceOn = store.get('voice2', false)")
R("store.set('voice',voiceOn)","store.set('voice2',voiceOn)")
R("store.set('voice',true)","store.set('voice2',true)")
# no emoji in buttons / chrome
R('aria-haspopup="true">🔊 Sound','aria-haspopup="true">Sound')
R('<span>🎵 Music</span>','<span>Music</span>'); R('<span>🔊 Sound effects</span>','<span>Sound effects</span>'); R('<span>🗣️ Narrator</span>','<span>Narrator voice</span>')
R('data-act="playVo" hidden>🔈 Hear the narrator','data-act="playVo" hidden>Hear the narrator')
R("${S.pendingLv?'⭐ Level up!':'🧳 Visit the merchant'","${S.pendingLv?'Level up!':'Visit the merchant'")
R('<span class="stars">💫</span>','')
R('❤️ ${S.hp} / ${S.maxHp}','HP ${S.hp} / ${S.maxHp}',4)
R('data-act="sortSuit">Sort ♠♥','data-act="sortSuit">Sort suit')
R('data-act="sortRank">Sort #','data-act="sortRank">Sort rank')
# merchant deal: animated hand-over with speech bubbles
i=s.index('function tradePanel(){'); j=s.index('function pathPanel(){')
s=s[:i]+'''function tradePanel(){
  S.phase='trade'; const t=S.trade, e=EQUIP[t.type], nm=eqName(t.type,t.tier), pw=e.atk?e.atk[t.tier]:e.def[t.tier];
  const talk=[`Ah, the ${nm}! A fine choice. That will be ${t.price} gold.`, ...t.trades.map(x=>`I'll buy your old ${x.name} for ${x.pay} gold.`), `${e.atk?'Swing it well':'May it keep you safe'}, hero!`];
  const rows=[`<div class="tl you">You pay <b class="neg">−${coin(t.price)}</b></div>`, ...t.trades.map(x=>`<div class="tl you">Sold your old ${x.name} <b class="pos">+${coin(x.pay)}</b></div>`)];
  openPanel(`<div class="cine-scene kb2 deal"><img src="${sceneImg('merchant')}" alt=""><span class="cine-title">A deal is struck</span>
      <div class="bubble-say" id="dealSay"><span id="capTxt"></span></div>
      <span class="deal-coins">${[0,1,2,3].map(k=>`<i style="animation-delay:${1.5+k*.12}s">${I('coin')}</i>`).join('')}</span>
      <span class="deal-item" style="animation-delay:${2.6+t.trades.length*1.6}s">${e.icon}</span></div>
    <div class="deal-sum" style="animation-delay:${3.4+t.trades.length*1.6}s">
      <div class="tl item"><span class="big-ic">${e.icon}</span><span><b>${nm}</b><span class="pw ${e.atk?'a':'d'}">+${pw} ${e.atk?'Attack':'Defense'}</span></span></div>
      ${rows.join('')}
    </div>
    <button class="btn big vic-btn" data-act="tradeOk" style="opacity:0;animation:rwIn .4s ease ${3.8+t.trades.length*1.6}s forwards">Back to the shop</button>`);
  $('panel').classList.add('cine');
  const say=(k)=>{ if(S.phase!=='trade'||!$('capTxt')) return; const b=$('dealSay'); b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); typeCaption(talk[k], talk[k].length/30); narrate(talk[k]); };
  say(0); setTimeout(()=>{ if(S.phase==='trade') coins(); },1600);
  t.trades.forEach((x,k)=>setTimeout(()=>{ say(k+1); if(S.phase==='trade') coins(); },2600+k*1600));
  setTimeout(()=>{ if(S.phase==='trade') anvil(); },2900+t.trades.length*1600);
  setTimeout(()=>say(talk.length-1),3300+t.trades.length*1600);
}
'''+s[j:]
css='''/* ---- buttons: dark inked plates, centered, readable ---- */
.btn,.tool,.buy,.mini-btn{text-align:center;justify-content:center;font-family:var(--f-num);font-weight:600;letter-spacing:.06em;text-transform:uppercase}
.btn.big,.vic-btn,.panel.parch .btn.big{background:linear-gradient(#2a1d16,#120d0b)!important;color:var(--gold)!important;border:2px solid #000!important;box-shadow:inset 0 0 0 1px rgba(242,182,50,.55),3px 3px 0 #000!important;font-family:var(--f-num)!important;font-weight:600;font-size:1.15rem!important;letter-spacing:.08em;text-shadow:1px 1px 0 #000}
.btn.big:hover,.vic-btn:hover{filter:brightness(1.25)}
.btn.atk{background:linear-gradient(#5a1510,#2c0907);color:#f3e6c8;border:2px solid #000;box-shadow:inset 0 0 0 1px rgba(255,110,80,.45),3px 3px 0 #000;font-family:var(--f-num);font-weight:600;font-size:1.2rem;letter-spacing:.1em;text-shadow:1px 1px 0 #000}
.btn.disc,.btn.ghost,.tool{background:linear-gradient(#241912,#120d0b);color:#e8d9bb;border:2px solid #000;box-shadow:inset 0 0 0 1px rgba(242,182,50,.22),2px 2px 0 #000;font-size:.82rem}
.btn:disabled{opacity:1;color:#6f604e;background:#15100d;box-shadow:inset 0 0 0 1px rgba(255,255,255,.06),2px 2px 0 #000;text-shadow:none}
.buy{border:1px solid #000;box-shadow:inset 0 0 0 1px rgba(242,182,50,.4)}
.buy:disabled{opacity:1;background:#5b5045;color:#e9dcc4;box-shadow:none}
.mini-btn.use{background:#120d0b;color:var(--gold);border:1px solid #000;box-shadow:inset 0 0 0 1px rgba(242,182,50,.5)}
.pathbtn,.innbtn{justify-content:center}
.pathbtn .inn-txt,.innbtn .inn-txt{text-align:center;align-items:center}
.pathbtn.quest{background:linear-gradient(#2a1d16,#120d0b);color:var(--gold);box-shadow:inset 0 0 0 1px rgba(242,182,50,.55),4px 4px 0 #000}
.pathbtn.quest .inn-txt b{color:var(--gold)} .pathbtn.quest .inn-txt small{color:#e8d9bb}
.pathbtn.hunt{background:linear-gradient(#1b2e2b,#0e1816);box-shadow:inset 0 0 0 1px rgba(43,179,166,.5),4px 4px 0 #000}
.innbtn{background:linear-gradient(#2a1d16,#120d0b);color:#e8d9bb;box-shadow:inset 0 0 0 1px rgba(242,182,50,.4),4px 4px 0 #000}
.innbtn .inn-txt b{color:var(--gold)} .innbtn .inn-txt small{color:#cdbb99}
.innbtn:disabled{background:#15100d}
.inn-ic{background:#f3e6c8}
.sndtog{font-family:var(--f-num);font-weight:600;letter-spacing:.05em;text-transform:uppercase;background:#1b1410;color:#e8d9bb;border:1px solid #000}
.sndmenu{background:#0f0b09}
/* centered text wherever it reads better */
.panel h2,.panel p,.eyebrow,.tipbox,.vic-sub,.kit-label,.story p,.panel .cine-cap p{text-align:center}
.panel .cine-cap p{justify-items:center}
.kit-label{justify-content:center}
.panel>.row{justify-content:center}
.tl.you{align-self:center}
.toast{text-align:center}
.info{justify-content:center;text-align:center}
.split-main>.row:first-child{justify-content:center!important;gap:12px}
/* deal scene */
.cine-scene.deal{aspect-ratio:16/9}
.bubble-say{position:absolute;z-index:3;left:4%;top:16%;max-width:52%;background:#f3e6c8;color:#16100d;border:3px solid #000;border-radius:16px;padding:8px 12px;font-weight:700;font-size:clamp(.85rem,2.4vw,1.05rem);line-height:1.3;text-align:center;box-shadow:3px 3px 0 #000;opacity:0}
.bubble-say::after{content:"";position:absolute;right:-16px;top:38%;border:9px solid transparent;border-left:14px solid #000}
.bubble-say::before{content:"";position:absolute;right:-10px;top:calc(38% + 2px);border:7px solid transparent;border-left:11px solid #f3e6c8;z-index:1}
.bubble-say.pop{animation:sayPop .35s cubic-bezier(.2,1.6,.4,1) forwards}
@keyframes sayPop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}
.deal-coins{position:absolute;inset:0;z-index:2;pointer-events:none}
.deal-coins i{position:absolute;left:6%;bottom:6%;width:34px;height:34px;opacity:0;animation:coinToMerchant .9s ease-in forwards}
.deal-coins .ico{width:100%;height:100%}
@keyframes coinToMerchant{0%{opacity:1;transform:translate(0,0) scale(1)}60%{opacity:1;transform:translate(42vw,-30%) scale(1.1)}100%{opacity:0;transform:translate(min(52vw,400px),-60%) scale(.6)}}
.deal-item{position:absolute;z-index:2;right:22%;top:52%;opacity:0;animation:itemToYou 1.1s cubic-bezier(.3,0,.3,1) forwards}
.deal-item .ico{width:72px;height:72px;filter:drop-shadow(0 0 14px rgba(255,210,90,.9))}
@keyframes itemToYou{0%{opacity:0;transform:scale(.4)}20%{opacity:1;transform:scale(1.1)}100%{opacity:1;transform:translate(calc(-1 * min(40vw,330px)),40%) scale(1.5) rotate(-12deg)}}
.deal-sum{display:flex;flex-direction:column;gap:8px;opacity:0;animation:rwIn .45s ease forwards}
.deal-sum .tl{opacity:1;animation:none}
'''
i=s.index('@media (prefers-reduced-motion:reduce)'); s=s[:i]+css+s[i:]
open(p,'w').write(s); print('ok', s.count('Brianna'))
