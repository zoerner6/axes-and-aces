p='game.html'; s=open(p).read()
def rep(a,b):
    global s
    assert a in s, 'MISSING: '+a[:90]; s=s.replace(a,b,1)
# challenge links carry the score
rep("const bragUrl = ()=>SITE+'b/'+(bragNow?bragNow.key:'game')+'.html';","""function bragQuery(){ if(!bragNow) return '';
  if(bragNow.key==='daily'&&S.dailyResult) return `?c=daily&d=${S.dailyResult.date}&s=${S.dailyResult.score}`;
  if(bragNow.key==='fallen'||bragNow.key==='level'||bragNow.key==='boss') return `?c=lvl&s=${S.level}&w=${(S.world||0)+1}`;
  return ''; }
const bragUrl = ()=>SITE+'b/'+(bragNow?bragNow.key:'game')+'.html'+bragQuery();""")
# reward for sharing (once a day)
rep("let bragCanvas=null, bragNow=null;","""let bragCanvas=null, bragNow=null;
function shareReward(){
  if(!S||S.daily) return; const k=todayKey(); if(store.get('aa_shareday','')===k) return; store.set('aa_shareday',k);
  setTimeout(()=>{ if(S.spells.length<3){ S.spells.push('potion'); itemSplash(I('potion'),'Thanks for sharing! Free potion',0,'+1',coins); }
    else { S.gold+=5; itemSplash(I('coin'),'Thanks for sharing! Free gold',0,'+5',coins); } render(); saveGame(); }, 600);
}""")
for act in ["case 'bragFb': {","case 'bragShare': {","case 'bragSave': {","case 'bragCopy': {"]:
    rep(act, act+" shareReward();")
rep("""<button class="btn big brag-fb" data-act="brag" data-kind="death">Share my score</button>""","""<button class="btn big brag-fb" data-act="brag" data-kind="death">Challenge a friend to beat me</button>""")
rep("""    <p class="menu-note">Tip: on Facebook, post the saved picture with the link so friends can tap it and play.</p>""","""    <p class="menu-note">${store.get('aa_shareday','')===todayKey()||(S&&S.daily)?'Tip: post the picture with the link so friends can tap it and play.':'<b>Share today and get a free potion!</b> Post the picture with the link so friends can tap it and play.'}</p>""")
# incoming challenge
rep("function start(data){","""/* someone shared a challenge link with us */
function readChallenge(){ try{ const q=new URLSearchParams(location.search), c=q.get('c'); if(!c) return null; const r={c, s:+q.get('s')||0, d:q.get('d')||'', w:+q.get('w')||1}; history.replaceState(null,'',location.pathname); return r; }catch(e){ return null; } }
function challengePanel(ch, after){
  const daily=ch.c==='daily'&&ch.d===todayKey();
  if(daily) store.set('aa_beat',{d:ch.d,s:ch.s});
  openPanel(`<div class="cine-scene"><img src="art/sc_merchant.webp" alt=""><span class="cine-title">You've been challenged!</span></div>
    <h2>${daily?`Beat ${fmt(ch.s)} points`:ch.c==='daily'?'A friend took on the Daily Challenge':`A friend reached level ${ch.s}`}</h2>
    <p>${daily?'A friend scored this in today\\'s Daily Challenge. Same monsters, same cards. Can you beat it?':ch.c==='daily'?'That challenge has ended, but today\\'s is waiting. Can you top your friend?':`They made it to level ${ch.s} in Quest ${ch.w}. Think you can go further?`}</p>
    ${ch.c==='daily'?'<button class="btn big daily-btn" data-act="daily">Take the Daily Challenge</button>':''}
    <button class="btn big ${ch.c==='daily'?'ghost':''}" data-act="chGo">${ch.c==='daily'?'Play the adventure instead':'Start my adventure'}</button>`);
  $('panel').classList.add('cine'); S.chAfter=after;
}
function start(data){""")
rep("  const sv=loadSave();\n  if(sv){ canSave=false; newRun(false); render(); titlePanel(sv); return; }\n  const first=!store.get('tutorialDone',false);",
    "  const sv=loadSave(), ch=readChallenge();\n  if(sv){ canSave=false; newRun(false); render(); if(ch){ challengePanel(ch,'title'); return; } titlePanel(sv); return; }\n  const first=!store.get('tutorialDone',false);\n  if(ch){ newRun(first); render(); challengePanel(ch,'story'); return; }")
rep("    case 'dailyQuit': dailyQuit(); break;","""    case 'dailyQuit': dailyQuit(); break;
    case 'chGo': { const sv=loadSave(); if(S.chAfter==='title'&&sv) titlePanel(sv); else storyPanel(); break; }""")
# score to beat shown in daily
rep("<div class=\"lines\"><div><span>Your level</span><b>${S.level}</b></div><div><span>Best today</span>",
    "<div class=\"lines\">${(()=>{const b=store.get('aa_beat',null);return b&&b.d===todayKey()?`<div><span>Friend's score to beat</span><b style=\"color:#ff8b7e\">${fmt(b.s)} points</b></div>`:''})()}<div><span>Your level</span><b>${S.level}</b></div><div><span>Best today</span>")
rep("  openPanel(`<div class=\"vic\"><div class=\"vic-title\">${D.wins>=5?'Champion!':'Challenge over'}</div>",
    "  const tb=store.get('aa_beat',null), beat=tb&&tb.d===D.key ? (score>tb.s?`<div class=\"beat win\">You beat your friend's ${fmt(tb.s)} points!</div>`:`<div class=\"beat\">Your friend's score: ${fmt(tb.s)}. So close!</div>`) : '';\n  openPanel(`<div class=\"vic\">${beat}<div class=\"vic-title\">${D.wins>=5?'Champion!':'Challenge over'}</div>")
# epic moments for monster hands
rep("  achOnHand(ev, played, dmg); if(S.daily) S.daily.atks++;","""  achOnHand(ev, played, dmg); if(S.daily) S.daily.atks++;
  if(ev.type==='sflush'&&ev.cards.some(c=>c.rank===14)&&ev.cards.some(c=>c.rank===13)) epicMoment('ROYAL FLUSH!','The rarest hand in poker');
  else if(ev.type==='sflush') epicMoment('STRAIGHT FLUSH!','Legendary hand');
  else if(ev.type==='four') epicMoment('FOUR OF A KIND!','Devastating');""")
rep("/* ---- daily challenge: same monsters","""/* ---- once-in-a-while hands get a huge, screenshot-worthy moment ---- */
function epicMoment(t, sub){
  const e=document.createElement('div'); e.className='epic'; e.innerHTML=`<span class="epic-rays"></span><b>${t}</b><small>${sub}</small>`;
  document.body.appendChild(e); confetti(['✨','🪙','⭐','♠','♥','♦','♣']); trumpetCall(); shake(); setTimeout(()=>e.remove(),2600);
}
/* ---- daily challenge: same monsters""")
i=s.rindex('</style>')
s=s[:i]+'''
.epic{position:fixed;inset:0;z-index:110;display:flex;flex-direction:column;align-items:center;justify-content:center;pointer-events:none;background:radial-gradient(circle,rgba(60,30,0,.55),rgba(0,0,0,.75));animation:epicIn 2.6s ease forwards}
.epic-rays{position:absolute;width:160vmax;height:160vmax;background:repeating-conic-gradient(rgba(255,210,90,.28) 0 8deg,transparent 8deg 16deg);animation:spin 9s linear infinite;-webkit-mask:radial-gradient(circle,#000 10%,transparent 55%);mask:radial-gradient(circle,#000 10%,transparent 55%)}
.epic b{position:relative;font-family:var(--f-title);font-weight:400;font-size:clamp(3rem,13vw,8rem);line-height:1;color:#ffd35c;text-shadow:5px 5px 0 #000,-2px -2px 0 #000,0 0 40px rgba(255,200,60,.9);transform:rotate(-4deg);animation:epicSlam .55s cubic-bezier(.2,1.6,.4,1) both;text-align:center}
.epic small{position:relative;margin-top:14px;font-family:var(--f-num);font-weight:700;letter-spacing:.2em;text-transform:uppercase;font-size:clamp(1rem,3vw,1.6rem);color:#fff;text-shadow:2px 2px 0 #000}
@keyframes epicIn{0%{opacity:0}8%{opacity:1}80%{opacity:1}100%{opacity:0}}
@keyframes epicSlam{0%{transform:scale(3) rotate(-4deg);opacity:0}100%{transform:scale(1) rotate(-4deg);opacity:1}}
.beat{background:#3d7a3a;color:#fff;font-family:var(--f-title);font-size:1.3rem;padding:6px 14px;border:3px solid #000;border-radius:10px;box-shadow:3px 3px 0 #000;text-align:center}
.beat:not(.win){background:#5a2a12}
.btn.daily-btn{background:linear-gradient(#5a3c0c,#2a1b06)!important;color:#ffd35c!important}
'''+s[i:]
open(p,'w').write(s); print('ok')
