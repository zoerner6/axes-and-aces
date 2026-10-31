p='game.html'; s=open(p).read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:90]); s=s.replace(a,b)
R("} else info.textContent = 'Tap your soldier, potions or spells. 🔒 = learn it from the merchant.';","} else info.textContent = '';")
R("(gold rim) always add 10 points","(gold cards marked +10) always add 10 points",2)
R('''`<span class="cn br">${RL(c.rank)}<i>${s.s}</i></span></button>`;''','''`<span class="cn br">${RL(c.rank)}<i>${s.s}</i></span>${c.rank===14?'<span class="ace10">+10</span>':''}</button>`;''')
R('''  openPanel(`<div class="eyebrow">Level up!</div><div class="big-icon">⭐</div>
    <h2>You reached level ${S.level}!</h2>''','''  openPanel(`<div class="lvl-scene"><span class="lvl-rays"></span>
      <span class="lvl-sparks">${Array.from({length:14},(_,k)=>`<i style="left:${6+k*6.6}%;animation-delay:${(k*.37)%2.4}s"></i>`).join('')}</span>
      <img class="lvl-hero" src="art/hero_t${Math.max(0,...['armor','helm','shield'].map(k=>S.eq[k]?S.eq[k].tier:0))}.webp" alt="Your soldier">
      <span class="lvl-title">Level up!</span><span class="lvl-num">LV ${S.level}</span></div>
    <h2 style="text-align:center">You reached level ${S.level}!</h2>''')
R("  S.phase='level'; trumpetCall();","  S.phase='level'; trumpetCall(); setTimeout(()=>{ if(S.phase==='level') narrate(`Level up! You are now level ${S.level}. Every attack hits harder.`); },600);")
css='''.info{min-height:0;font-size:.8rem;line-height:1.25}
.info:empty{display:none}
.card.king{background:linear-gradient(160deg,#ffe9a0,#f2b632 55%,#d99a1c);border:2.5px solid #14100e;box-shadow:0 3px 0 rgba(0,0,0,.35)}
.card.king.sel{box-shadow:0 0 0 3px #fff,0 6px 0 rgba(0,0,0,.3)}
.ace10{position:absolute;left:50%;bottom:4%;transform:translateX(-50%);font-family:var(--f-num);font-weight:700;font-size:clamp(9px,2.6vw,14px);background:#14100e;color:#ffd35c;border-radius:4px;padding:0 4px;line-height:1.25;white-space:nowrap}
@media (min-width:521px){ .ace10{left:28%} }
/* level up scene */
.lvl-scene{position:relative;height:250px;display:grid;place-items:center;overflow:hidden;border:3px solid #000;border-radius:10px;box-shadow:5px 5px 0 #000;background:radial-gradient(circle at 50% 62%,#6b4612,#140e0a 70%)}
.lvl-rays{position:absolute;width:220%;aspect-ratio:1;left:-60%;top:-80%;background:repeating-conic-gradient(rgba(255,210,90,.3) 0 9deg,transparent 9deg 18deg);animation:spin 16s linear infinite;-webkit-mask:radial-gradient(circle,#000 18%,transparent 60%);mask:radial-gradient(circle,#000 18%,transparent 60%)}
.lvl-hero{position:relative;height:205px;width:auto;max-width:none;animation:lvlGrow 1.7s cubic-bezier(.2,1.4,.4,1) both,lvlShine 2.4s 1.7s ease-in-out infinite}
@keyframes lvlGrow{0%{transform:scale(.62) translateY(20px);filter:brightness(.5) saturate(.6)}55%{transform:scale(1.2);filter:brightness(2.6) drop-shadow(0 0 34px #ffd66b)}100%{transform:scale(1.08);filter:brightness(1.12) drop-shadow(0 0 16px #ffc83d)}}
@keyframes lvlShine{0%,100%{transform:scale(1.08);filter:brightness(1.12) drop-shadow(0 0 16px #ffc83d)}50%{transform:scale(1.11);filter:brightness(1.4) drop-shadow(0 0 30px #ffe08a)}}
.lvl-title{position:absolute;top:10px;left:50%;transform:translateX(-50%) rotate(-3deg);font-family:var(--f-title);font-size:2rem;background:var(--gold);color:#000;border:3px solid #000;padding:0 16px;box-shadow:3px 3px 0 #000;white-space:nowrap;animation:lvlPop .5s .9s cubic-bezier(.2,1.6,.4,1) both}
.lvl-num{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);font-family:var(--f-num);font-weight:700;font-size:1.3rem;background:var(--hp);color:#fff;border:3px solid #000;border-radius:999px;padding:0 16px;box-shadow:3px 3px 0 #000;animation:lvlPop .5s 1.3s cubic-bezier(.2,1.6,.4,1) both}
@keyframes lvlPop{from{opacity:0;scale:.3}}
.lvl-sparks{position:absolute;inset:0;pointer-events:none}
.lvl-sparks i{position:absolute;bottom:-8px;width:5px;height:5px;border-radius:50%;background:#ffe08a;box-shadow:0 0 8px 3px rgba(255,200,80,.8);animation:spark 2.4s ease-out infinite}
@keyframes spark{0%{transform:translateY(0);opacity:0}15%{opacity:1}100%{transform:translateY(-240px);opacity:0}}
'''
i=s.index('@media (prefers-reduced-motion:reduce)'); s=s[:i]+css+s[i:]
open(p,'w').write(s); print('ok')
