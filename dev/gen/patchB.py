import sys
p=sys.argv[1]; s=open(p).read()
def R(a,b):
    global s
    assert s.count(a)==1, (s.count(a), a[:90])
    s=s.replace(a,b)
i=s.index('  <section class="kit2">'); j=s.index('  <div class="info" id="info"></div>')
s=s[:i]+'''  <section class="satchel">
    <div class="ribbon"><span class="lv">🎖️ Lv <b id="lvlNum">1</b></span><div class="xp" aria-label="Experience"><i id="xpBar"></i><span id="xpNum">⭐ 0 EXP</span></div><span class="gold">💰 <b id="goldNum2">3</b></span></div>
    <div class="kitB">
      <button class="med" id="gearBtn" data-act="soldier" aria-label="Your soldier and gear"><span class="oval" id="miniSold"></span><span class="ad"><span class="a">⚔ <b id="atkNum">+0</b></span><span class="d">🛡 <b id="defNum">+0</b></span></span></button>
      <div class="pouch" id="spellBox"><b>Potions</b><div class="rings" id="spells"></div></div>
      <div class="pouch"><b>Wizard</b><div class="rings" id="books"></div></div>
      <div class="pouch"><b>Cleric</b><div class="rings" id="heals"></div></div>
    </div>
  </section>
'''+s[j:]
# CSS for the satchel
R('''@media (max-height:700px){''','''/* ---- Leather Satchel: gear, stats, potions and spells ---- */
.satchel{--leather:#5a3420;--leather2:#3f2416;--stitch:#d9a86a;--brass:#d6a443;--sheet:#f2e2bd;--sink:#2a170d;
  display:flex;flex-direction:column;gap:6px;background:linear-gradient(#4a2a1a,#2e1a10);border:2px solid #1c0f08;border-radius:14px;padding:7px}
.ribbon{display:grid;grid-template-columns:auto 1fr auto;gap:8px;align-items:center;background:var(--leather2);border:2px dashed var(--stitch);border-radius:11px;padding:4px 9px}
.ribbon .lv{display:flex;align-items:center;gap:4px;font-family:var(--f-title);font-size:1.1rem;color:var(--brass);white-space:nowrap}
.ribbon .lv b,.ribbon .gold b{font-family:var(--f-num);font-weight:700;color:#fff}
.ribbon .gold{display:flex;align-items:center;gap:4px;font-size:1.05rem;white-space:nowrap}
.ribbon .gold b{color:var(--brass);font-size:1.15rem}
.ribbon .xp{position:relative;height:17px;border-radius:999px;background:#24130b;border:2px solid var(--brass);overflow:hidden;min-width:0}
.ribbon .xp i{position:absolute;left:0;top:0;bottom:0;width:0;background:linear-gradient(90deg,#7a54c8,#b892ff);transition:width .5s}
.ribbon .xp span{position:absolute;inset:0;display:grid;place-items:center;font-family:var(--f-num);font-size:.7rem;font-weight:600;color:#fff;text-shadow:0 1px 0 #000;white-space:nowrap}
.kitB{display:grid;grid-template-columns:minmax(88px,1.15fr) repeat(3,minmax(0,1fr));gap:6px}
.med{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:none;border:0;padding:0;min-width:0}
.med:active .oval{transform:translateY(2px)}
.oval{width:min(100%,96px);aspect-ratio:96/118;border-radius:50% / 46%;background:radial-gradient(ellipse at 50% 40%,#f6e7c3,#d8bf8c);border:4px solid var(--brass);box-shadow:inset 0 0 0 2px #7a5208,0 3px 0 #1c0f08;overflow:hidden;display:flex;justify-content:center;align-items:flex-end;box-sizing:border-box}
.oval img{height:96%;width:auto;max-width:none}
.ad{display:flex;gap:3px;font-family:var(--f-num);font-weight:700;font-size:.8rem;flex-wrap:wrap;justify-content:center}
.ad>span{padding:0 6px;border-radius:999px;color:#2a1608;white-space:nowrap}
.ad b{font-weight:700}
.ad .a{background:#f0a48f}.ad .d{background:#a9cdf5}
.pouch{background:var(--leather);border:2px dashed var(--stitch);border-radius:11px 11px 16px 16px;padding:4px 3px 6px;display:flex;flex-direction:column;align-items:center;gap:4px;min-width:0}
.pouch>b{font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--stitch);font-weight:800}
.rings{display:flex;flex-direction:column;gap:4px;align-items:center}
.pouch .slot,.pouch .slot.spell,.pouch .slot.book,.pouch .slot.heal{width:38px;height:38px;min-height:0;padding:0;border-radius:50%;border:3px solid var(--brass);background:var(--sink);font-size:1.15rem;box-shadow:inset 0 2px 4px rgba(0,0,0,.6);color:#fff}
.pouch .slot.empty{border-color:#6b4a2c;opacity:.6;box-shadow:inset 0 2px 4px rgba(0,0,0,.6)}
.pouch .slot.locked{font-size:.72rem!important;opacity:.55}
.pouch .slot.on{outline:3px solid #fff;outline-offset:1px}
/* soldier sheet (popup and merchant) */
.sheetB{display:grid;grid-template-columns:130px 1fr;gap:10px;align-items:center;color:#2a1608}
.sh-fig img{display:block;height:220px;width:auto;max-width:100%;margin:0 auto}
.ledger{display:flex;flex-direction:column;gap:6px;min-width:0}
.lg{display:grid;grid-template-columns:24px 1fr auto;gap:2px 6px;align-items:center;border-bottom:1px dashed #b88a4a;padding-bottom:5px}
.lg>span{font-size:1.05rem}
.lg b{font-size:.9rem;line-height:1.1}
.lg b small{display:block;font-weight:600;font-size:.72rem;color:#7a5a3a}
.lg em{font-style:normal;font-family:var(--f-num);font-weight:700;font-size:.9rem;white-space:nowrap}
.lg em.a{color:#b3282b}.lg em.d{color:#2a5ea8}
.pips{grid-column:2/4;display:flex;gap:3px}
.pips i{width:14px;height:6px;border-radius:3px;background:#d8c59c}
.pips i.on{background:#7a5208}
.lg.empty{opacity:.5}
.totB{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;font-family:var(--f-num);font-weight:700;font-size:1.1rem;color:#2a1608}
.totB span{padding:3px 14px;border-radius:999px;border:2px solid #2a1608}
.totB .a{background:#f0a48f}.totB .d{background:#a9cdf5}
.sheetcard{background:#f2e2bd;background-image:radial-gradient(ellipse at 30% 0%,rgba(255,255,255,.5),transparent 60%);border:3px solid #7a5208;box-shadow:0 0 0 3px #3f2416;border-radius:14px;padding:12px;display:flex;flex-direction:column;gap:10px}
.panel.parch{background:#3f2416;border-color:#d9a86a;border-style:dashed}
.panel.parch h2{text-align:center}
.split-side .sheetB{grid-template-columns:1fr}
.split-side .sh-fig img{height:170px}
@media (max-width:700px){ .split-side .sheetB{grid-template-columns:96px 1fr} .split-side .sh-fig img{height:150px} }
@media (max-width:380px){ .pouch .slot,.pouch .slot.spell,.pouch .slot.book,.pouch .slot.heal{width:34px;height:34px;font-size:1rem} }
@media (max-height:700px){''')
R('''  $('xpNum').textContent = S.xp; $('lvlNum').textContent = S.level; $('goldNum2').textContent = S.gold;''',
'''  { const lo=cumNeed(S.level-1), hi=cumNeed(S.level); $('xpBar').style.width=Math.max(0,Math.min(100,(S.xp-lo)/(hi-lo)*100))+'%'; $('xpNum').textContent=`⭐ ${S.xp} / ${hi} EXP`; }
  $('lvlNum').textContent = S.level; $('goldNum2').textContent = S.gold;''')
i=s.index('function soldierCard(){'); j=s.index('function soldierPanel(){')
s=s[:i]+'''function soldierCard(){
  const pips=t=>`<div class="pips">${[1,2,3,4,5].map(n=>`<i class="${n<=t?'on':''}"></i>`).join('')}</div>`;
  const rows=SLOTS.map(([k,label])=>{ const it=S.eq[k];
    if(k==='off'&&twoHanded()) return `<div class="lg empty"><span>🚫</span><b>${label}<small>Both hands on your axe</small></b><em>—</em>${pips(0)}</div>`;
    if(!it) return `<div class="lg empty"><span>${({main:'⚔️',off:'🗡️',shield:'🛡️',helm:'⛑️',armor:'🦺'})[k]}</span><b>${label}<small>Empty</small></b><em>—</em>${pips(0)}</div>`;
    const e=EQUIP[it.type];
    return `<div class="lg"><span>${e.icon}</span><b>${eqName(it.type,it.tier)}</b><em class="${e.atk?'a':'d'}">+${e.atk?e.atk[it.tier]:e.def[it.tier]}</em>${pips(it.tier)}</div>`; }).join('');
  return `<div class="sheetcard">
    <div class="sheetB"><div class="sh-fig">${soldierSVG()}</div><div class="ledger">${rows}</div></div>
    <div class="totB"><span class="a">⚔ Attack +${weaponPts()}</span><span class="d">🛡 Defense +${defense()}</span></div>
  </div>`;
}
'''+s[j:]
R('''  openPanel(`<div class="eyebrow">Your gear</div><h2>Your soldier</h2>${soldierCard()}''','''  openPanel(`<h2>Your soldier</h2>${soldierCard()}''')
R('''    <button class="btn big vic-btn" data-act="close">Back</button>`);
}''','''    <button class="btn big vic-btn" data-act="close">Back</button>`); $('panel').classList.add('parch');
}''')
R('''$('panel').classList.remove('wide');''','''$('panel').classList.remove('wide','parch');''')
open(p,'w').write(s); print('ok')
