p='game.html'; s=open(p).read()
def rep(a,b):
    global s
    assert a in s, 'MISSING: '+a[:90]; s=s.replace(a,b,1)
# potion counter
rep("    if(id==='potion'){ healMe(150); soothe(); }","    if(id==='potion'){ healMe(150); soothe(); lifeAdd(L=>{L.potions++;}); if(life().potions>=10) unlock('potions10'); }")
# clue for later worlds
rep("    const clue=['","    const clue=(S.world||0)>0 ? worldClue() : ['")
rep("/* ================= travelers and finds appear where Edward actually is ================= */","""/* ================= travelers and finds appear where Edward actually is ================= */
function worldClue(){ const a=areaOf(), b=MONSTERS['boss_'+a], st=QUEST_STEPS[Math.min(QUEST_STEPS.length-1,a*3)];
  const lines=[`"${b?b.name:'Something terrible'} waits up ahead. ${st?st.why:''}. Be ready."`, `"I barely escaped ${b?b.name:'it'}. ${st?st.why:''}, and nobody who went has come back."`, `"You're heading for ${b?b.name:'the beast'}? Then listen: ${st?st.why.toLowerCase():'stay sharp'}."`];
  return lines[rnd(lines.length)]; }""")
# fight start HP for "untouched"
rep("  S.fight = {id, hp:d.hp, max:d.hp, block:0, turn:0, frozen:false,","  S.fight = {id, hp:d.hp, max:d.hp, block:0, turn:0, frozen:false, hp0:S.hp, atks:0,")
# every attack
rep("  if(dmg>S.stats.best){ S.stats.best=dmg; S.stats.bestName=HANDS[ev.type].name; }","  if(dmg>S.stats.best){ S.stats.best=dmg; S.stats.bestName=HANDS[ev.type].name; }\n  achOnHand(ev, played, dmg); if(S.daily) S.daily.atks++;")
# wins
rep("  if(ups){ S.lvlReport={ups, gifts}; }","""  if(ups){ S.lvlReport={ups, gifts}; }
  achOnWin(d);
  if(S.daily){ S.daily.wins++; S.pendingLv=0; S.lvlReport=null; S.phase='dailyWin';
    openPanel(`<div class="vic"><div class="vic-title">Victory!</div><div class="vic-sub">Daily fight ${S.daily.n+1} of 5 won · ${S.daily.atks} attacks so far</div>
      <div class="vic-hp"><div class="hpbar mehp"><i style="width:${Math.max(0,S.hp/S.maxHp*100)}%"></i><span>HP ${S.hp} / ${S.maxHp}</span></div></div>
      <button class="btn big vic-btn" data-act="dailyNext">${S.daily.n+1>=5?'See my score':'Next fight'}</button></div>`); return; }""")
rep("async function defeat(){\n  await wait(400); busy=false; S.phase='over'; clearSave();","async function defeat(){\n  await wait(400); busy=false;\n  if(S.daily){ dailyDone(); return; }\n  lifeAdd(L=>{L.deaths++;}); S.phase='over'; clearSave();")
rep("  S.world=(S.world||0)+1; S.knighted=true; loadWorld(S.world);","  S.world=(S.world||0)+1; S.knighted=true; loadWorld(S.world); achOnQuest();")
# brag buttons
rep("""    <button class="btn big vic-btn" data-act="afterVictory">${S.pendingLv?'Level up!':'Visit the merchant'}</button>""",
    """    ${w.boss?'<button class="btn big brag-fb" data-act="brag" data-kind="boss">Brag about this win</button>':''}
    <button class="btn big vic-btn" data-act="afterVictory">${S.pendingLv?'Level up!':'Visit the merchant'}</button>""")
rep("""    <button class="btn big vic-btn" data-act="lvlOk" style="opacity:0;animation:rwIn .4s ease 1.4s forwards">Visit the merchant</button>`);""",
    """    <div class="row" style="width:100%;opacity:0;animation:rwIn .4s ease 1.4s forwards"><button class="btn big brag-fb" data-act="brag" data-kind="level">Brag</button><button class="btn big vic-btn" data-act="lvlOk" style="flex:2">Visit the merchant</button></div>`);""")
rep("""    <button class="btn big" data-act="storyNext">${btn}</button></div>""","""    ${last&&S.story.key==='end'?'<button class="btn big brag-fb" data-act="brag" data-kind="quest">Brag</button>':''}<button class="btn big" data-act="storyNext">${btn}</button></div>""")
rep("${summary()}${sv?","<button class=\"btn big brag-fb\" data-act=\"brag\" data-kind=\"death\">Share my score</button>${summary()}${sv?")
rep("""      <button class="btn big" data-act="close">Continue playing</button>""","""      <button class="btn big" data-act="close">Continue playing</button>
      <button class="btn big ghost daily" data-act="daily">Daily Challenge</button>
      <button class="btn big ghost" data-act="ach">Achievements and stats</button>""")
rep("""    <button class="btn big newgame" data-act="newGame">New game</button>`);""","""    <button class="btn big ghost daily" data-act="daily">Daily Challenge</button>
    <button class="btn big newgame" data-act="newGame">New game</button>`);""")
# actions
rep("    case 'close': closePanel(); resumePhase(); break;","""    case 'close': closePanel(); resumePhase(); break;
    case 'brag': { const ov=!$('overlay').hidden; S.bragPrev = ov ? {html:$('panel').innerHTML, cls:$('panel').className} : null; bragPanel(t.dataset.kind, t.dataset.id); break; }
    case 'bragClose': { const pv=S.bragPrev; S.bragPrev=null; if(pv){ $('panel').innerHTML=pv.html; $('panel').className=pv.cls; } else closePanel(); break; }
    case 'bragFb': { const u='https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(bragUrl())+'&quote='+encodeURIComponent(bragText()); const a=document.createElement('a'); a.href=u; a.target='_blank'; a.rel='noopener'; document.body.appendChild(a); a.click(); a.remove(); break; }
    case 'bragShare': { bragBlob().then(b=>{ const file=b&&new File([b],'axes-and-aces.jpg',{type:'image/jpeg'});
        if(file && navigator.canShare && navigator.canShare({files:[file]})) navigator.share({files:[file], text:bragText()+' '+bragUrl()}).catch(()=>{});
        else if(navigator.share) navigator.share({title:'Axes & Aces', text:bragText(), url:bragUrl()}).catch(()=>{});
        else toast('Use "Save picture", then post it with the link'); }); break; }
    case 'bragSave': { bragBlob().then(b=>{ if(!b) return; const u=URL.createObjectURL(b), a=document.createElement('a'); a.href=u; a.download='axes-and-aces-brag.jpg'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(u),4000); toast('Picture saved'); }); break; }
    case 'bragCopy': { const txt=bragText()+' '+bragUrl(); (navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(()=>toast('Link copied')).catch(()=>toast(bragUrl())); break; }
    case 'ach': achPanel(); break;
    case 'daily': startDaily(); break;
    case 'dailyGo': closePanel(); fightIntro(); break;
    case 'dailyNext': dailyNextFight(); break;
    case 'dailyQuit': dailyQuit(); break;""")
open(p,'w').write(s); print('ok')
