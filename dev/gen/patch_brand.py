p='game.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert a in s, 'MISSING: '+a[:80]; s=s.replace(a,b,cnt)
# --- no emoji ---
rep("'A goblin! 👺 The red bar","'A goblin! The red bar")
rep("return '😵 Startled: skips its first move';","return `${I('skull')} Startled: skips its first move`;")
rep("return '❄️ Frozen: skips its next move';","return `${I('frost')} Frozen: skips its next move`;")
rep("<b>💚 Healing round:</b>","<b>${I('cleric')} Healing round:</b>")
rep("say(`😮‍💨 You catch your breath","say(`You catch your breath")
rep("foeBanner('😵 Startled!',","foeBanner('Startled!',")
rep("foeBanner('❄️ Frozen!',","foeBanner('Frozen!',")
s=s.replace("say(`❄️ The ","say(`The ")
rep("return `💰 You found a coin pouch:","return `${I('bag')} You found a coin pouch:")
rep("return `📖 All that fighting paid off:","return `${I('level')} All that fighting paid off:")
rep("gift='a <b>Healing Potion</b> 🧪';","gift='a <b>Healing Potion</b>';")
rep("confetti(['🐉','🍻','⭐','🪙','⚔️']);","confetti();")
rep("<div class=\"big-icon\">🏆</div>","<div class=\"big-icon\"><img class=\"ico\" src=\"art/hero_t5.webp\" alt=\"\" style=\"width:auto;height:120px\"></div>")
rep("confetti(['✨','🪙','⭐','♠','♥','♦','♣']);","confetti();")
rep("""function confetti(bits=['⚔️','✨','🪙','🍺','⭐']){
  if(reduced()) return;
  for(let i=0;i<36;i++){
    const s=document.createElement('div'); s.className='confetti'; s.textContent=bits[rnd(bits.length)];""","""/* celebration burst: the game's own gold coins and card suits, never emoji */
function confetti(){
  if(reduced()) return; const bits=['coin','coin','coin','♠','♥','♦','♣'];
  for(let i=0;i<36;i++){
    const s=document.createElement('div'); s.className='confetti'; const b=bits[rnd(bits.length)];
    if(b==='coin') s.innerHTML=`<img src="art/i_coin.webp" alt="" style="width:28px;height:28px">`; else { s.textContent=b+'\\uFE0E'; s.style.color=(b==='♥'||b==='♦')?'#e2342a':'#ffd35c'; s.style.webkitTextStroke='1px #000'; }""")
for a in ["$('foeBlock').textContent = `🛡️ ${f.block}`;","$('myBlock').textContent = `🛡️ ${S.block}`;","$('foeBlock').textContent=`🛡️ ${f.block}`;","$('myBlock').textContent=`🛡️ ${S.block}`;"]:
    rep(a, a.replace("textContent","innerHTML").replace("🛡️ ","${I('shield')} "))
rep("$('intent').textContent = intentText(mv);","$('intent').innerHTML = intentText(mv);")
import re
m=re.search(r"return mv\.k==='atk' \? `⚔️ Next: attacks for \$\{mv\.n\}` : mv\.k==='blk' \? `🛡️ Next: raises a shield of \$\{mv\.n\}` : `💚 Next: will heal itself for \$\{mv\.n\}`;",s)
assert m
s=s.replace(m.group(0),"return mv.k==='atk' ? `${I('attack')} Next: attacks for ${mv.n}` : mv.k==='blk' ? `${I('shield')} Next: raises a shield of ${mv.n}` : `${I('heart')} Next: will heal itself for ${mv.n}`;",1)

# --- Old Bram tips as a comic panel ---
rep("bub.innerHTML = `<div class=\"who\">Old Bram · tip ${S.coach+1} of ${STEPS.length}</div><div>${html}</div>`+\n    `<div class=\"bb\"><button class=\"skip\" data-act=\"skipTutorial\">Skip tips</button>${st.btn?`<button data-act=\"coachNext\">${st.btn}</button>`:''}</div><span class=\"arrow\"></span>`;",
    "bub.innerHTML = `<img class=\"bram\" src=\"art/p_bram.webp\" alt=\"Old Bram\"><div class=\"who\"><b>Old Bram</b><span>Tip ${S.coach+1} of ${STEPS.length}</span></div><div class=\"btxt\">${html}</div>`+\n    `<div class=\"bb\"><button class=\"skip\" data-act=\"skipTutorial\">Skip tips</button>${st.btn?`<button data-act=\"coachNext\">${st.btn}</button>`:''}</div><span class=\"arrow\"></span>`;")

# --- How to play rewritten ---
a=s.index('<ol class="howto">'); b=s.index('</ol>',a)+5
s=s[:a]+'''<ol class="howto steps">
      <li><span class="hn">1</span><div><b>Discard first.</b> Every turn you get 1 discard. Swap up to 5 cards that don't help, to fish for a better hand. The monster doesn't attack when you discard.</div></li>
      <li><span class="hn">2</span><div><b>Pick your best poker hand</b> (up to 5 cards). The damage shows above your cards before you attack. Stuck? Tap <b>Hint</b>.</div></li>
      <li><span class="hn">3</span><div><b>Tap Attack!</b> Then the monster hits back. Its next move shows under its name. Then you get a whole new hand.</div></li>
      <li><span class="hn">${I('coin')}</span><div><b>Aces</b> (gold cards) always add ${aceBonus()} points right now, even as extra cards. Bosses have a rule: cards marked with a red ✖ don't count for damage.</div></li>
      <li><span class="hn">${I('heart')}</span><div><b>Health doesn't refill by itself.</b> Rest at the inn, drink a potion, or tap <b>Rest</b> in a fight (the monster gets a free hit). Too tough? <b>Run</b> and train first.</div></li>
      <li><span class="hn">${I('level')}</span><div><b>Level up</b> to multiply every hit. Buy weapons and armor from the merchant, and learn spells from level 3.</div></li>
      <li><span class="hn">${I('map')}</span><div><b>Rescue Anna,</b> get knighted, then take on 9 more quests and the Endless Abyss.</div></li>
    </ol>'''+s[b:]

# --- encounter speech bubble: never on top of the title tag ---
CSS='''
/* brand pass: no text on text, tips as comic panels, how-to as numbered steps */
.enc-say,.enc-say.you{top:16%!important;bottom:auto!important;left:auto!important;right:3%!important;width:44%!important}
@media (max-width:420px){ .enc-say,.enc-say.you{top:24%!important;width:56%!important} }
#bubble{display:grid;grid-template-columns:64px 1fr;grid-template-areas:"pic who" "pic txt" "bb bb";column-gap:12px;background:#f3e6c8;color:#16100d;border:3px solid #000;border-radius:12px;box-shadow:5px 5px 0 #000;padding:12px 14px}
#bubble .bram{grid-area:pic;width:64px;height:64px;object-fit:cover;object-position:top;border-radius:50%;border:3px solid #000;background:#3a2414;box-shadow:2px 2px 0 #000;align-self:start}
#bubble .who{grid-area:who;display:flex;align-items:baseline;gap:8px;margin-bottom:2px;text-transform:none;letter-spacing:0;color:inherit}
#bubble .who b{font-family:var(--f-title);font-weight:400;font-size:1.25rem;color:#8e1a14}
#bubble .who span{font-family:var(--f-num);font-weight:700;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:#7a6650}
#bubble .btxt{grid-area:txt;line-height:1.4}
#bubble .bb{grid-area:bb;margin-top:10px}
#bubble .bb button:not(.skip){background:linear-gradient(#ffd35c,#d89a14);color:#16100d;border:3px solid #000;border-radius:8px;box-shadow:3px 3px 0 #000;font-family:var(--f-num);font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:6px 16px}
#bubble .bb button.skip{color:#7a6650;font-weight:700}
.howto.steps{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px;width:100%}
.howto.steps li{display:grid;grid-template-columns:40px 1fr;gap:12px;align-items:start;background:#120d0b;border:2px solid #000;border-radius:10px;padding:10px 12px;line-height:1.4}
.howto.steps .hn{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 35% 30%,#ffe9a0,#f2b632 55%,#9b7a10);border:3px solid #000;box-shadow:2px 2px 0 #000;font-family:var(--f-title);font-size:1.4rem;color:#fff;-webkit-text-stroke:1px #000;paint-order:stroke fill}
.howto.steps .hn .ico{width:26px;height:26px}
.howto.steps b{color:var(--gold)}
.chip .ico,#intent .ico,#foeBlock .ico,#myBlock .ico,.info .ico{width:18px;height:18px;vertical-align:-3px}
/* story and merchant scenes on short desktop screens: shrink the whole picture instead of cropping heads */
@media (max-height:860px) and (min-aspect-ratio:5/4){
  .panel.cine .cine-scene{height:auto!important;aspect-ratio:16/9!important;max-height:none!important;width:min(100%,calc(36vh * 16 / 9));align-self:center}
  .panel.cine .cine-scene.death{aspect-ratio:16/10!important}
}
.cine-scene>img:first-child{object-position:center 30%}
'''
i=s.rindex('</style>'); s=s[:i]+CSS+s[i:]
open(p,'w').write(s); print('ok')
