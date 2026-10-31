p='game.html'; s=open(p).read()
def rep(a,b):
    global s
    assert a in s, 'MISSING: '+a[:90]; s=s.replace(a,b,1)
JS=r'''
/* ================= online: leaderboards and cloud saves (Netlify functions + Neon) ================= */
const API='/.netlify/functions/';
async function api(path, body){
  const r=await fetch(API+path, body?{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}:{});
  const j=await r.json().catch(()=>({})); if(!r.ok) throw new Error(j.error||'Could not reach the server'); return j;
}
const myName = ()=>store.get('aa_name','');
function nameRow(){ return `<div class="name-row"><label for="lbName">Your name</label><input id="lbName" maxlength="20" placeholder="Sir Edward" value="${(myName()||'').replace(/"/g,'')}"></div>`; }
function readName(){ const v=(($('lbName')||{}).value||'').trim().slice(0,20); if(v) store.set('aa_name',v); return v; }
function scoreList(rows, mine){ if(!rows||!rows.length) return '<p class="menu-note">No scores yet. Be the first!</p>';
  return `<ol class="lb">${rows.map((r,i)=>`<li class="${mine&&r.name===mine?'me':''}"><span>${i+1}</span><b>${String(r.name).replace(/</g,'')}</b><em>${fmt(r.score)}</em></li>`).join('')}</ol>`; }
async function lbPanel(board){
  board=board||'daily';
  openPanel(`<div class="eyebrow">Hall of Heroes</div><h2>Leaderboard</h2>
    <div class="row lb-tabs"><button class="btn ${board==='daily'?'':'ghost'}" data-act="lb" data-board="daily">Today's Daily Challenge</button><button class="btn ${board==='level'?'':'ghost'}" data-act="lb" data-board="level">Highest level</button></div>
    <div id="lbList"><p class="menu-note">Loading...</p></div>
    <button class="btn big" data-act="close">Back</button>`);
  try{ const j=await api(`get-scores?board=${board}&day=${todayKey()}`); const el=$('lbList'); if(el) el.innerHTML=scoreList(j.scores, myName()); }
  catch(e){ const el=$('lbList'); if(el) el.innerHTML=`<p class="menu-note">The leaderboard isn't available here. Play at AxesAndAces.com to join it.</p>`; }
}
async function postScore(board, score, btn){
  const name=readName(); if(!name){ toast('Type your name first'); const i=$('lbName'); if(i) i.focus(); return; }
  if(btn){ btn.disabled=true; btn.textContent='Posting...'; }
  try{ await api('add-score',{board, day:todayKey(), name, score}); if(btn) btn.textContent='Posted ✓'; toast('Score posted!');
    const j=await api(`get-scores?board=${board}&day=${todayKey()}`); const el=$('lbList'); if(el) el.innerHTML=scoreList(j.scores, name); }
  catch(e){ if(btn){ btn.disabled=false; btn.textContent='Try again'; } toast(e.message); }
}
/* cloud save: a private code you can type on any device */
function cloudCode(){ let c=store.get('aa_cloud',''); if(!c){ const a='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; c=Array.from(crypto.getRandomValues(new Uint8Array(16)),x=>a[x%a.length]).join(''); store.set('aa_cloud',c); } return c; }
const prettyCode = c=>c.match(/.{1,4}/g).join('-');
function cloudPanel(){
  const c=cloudCode();
  openPanel(`<div class="eyebrow">Play on any device</div><h2>Cloud save</h2>
    <p>Your private save code. Write it down or copy it. Type it on your phone or another computer to pick up where you left off.</p>
    <div class="cloud-code">${prettyCode(c)}</div>
    <div class="row"><button class="btn big" data-act="cloudSave">Save to cloud</button><button class="btn big ghost" data-act="cloudCopy">Copy code</button></div>
    <div class="name-row"><label for="cloudIn">Load a save code</label><input id="cloudIn" maxlength="24" placeholder="ABCD-EFGH-JKLM-NPQR"></div>
    <button class="btn big ghost" data-act="cloudLoad">Load from cloud</button>
    <p class="menu-note" id="cloudMsg"></p>
    <button class="btn big" data-act="close">Back</button>`);
}
async function cloudSave(quiet){
  if(!S||S.daily) return; const m=$('cloudMsg');
  try{ await api('save-game',{code:cloudCode(), data:{S, at:Date.now()}}); if(!quiet){ toast('Saved to the cloud'); if(m) m.textContent='Saved. Use your code on any device.'; } }
  catch(e){ if(!quiet){ toast(e.message); if(m) m.textContent=e.message; } }
}
async function cloudLoad(){
  const raw=(($('cloudIn')||{}).value||'').toUpperCase().replace(/[^A-Z0-9]/g,''), m=$('cloudMsg');
  if(raw.length<12){ if(m) m.textContent='Type the 16-letter code.'; return; }
  try{ const j=await api('load-game?code='+raw); const sv=j.data; if(!sv||!sv.S) throw new Error('No save found for that code');
    store.set('aa_cloud',raw); try{ localStorage.setItem('aa_save', JSON.stringify(sv)); }catch(e){}
    canSave=true; closePanel(); start({S:sv.S}); toast('Loaded your cloud save'); }
  catch(e){ if(m) m.textContent=e.message; }
}
'''
rep("/* ---- once-in-a-while hands get a huge, screenshot-worthy moment ---- */", JS+"\n/* ---- once-in-a-while hands get a huge, screenshot-worthy moment ---- */")
# menu entries
rep("""      <button class="btn big ghost" data-act="ach">Achievements and stats</button>""","""      <button class="btn big ghost" data-act="ach">Achievements and stats</button>
      <button class="btn big ghost" data-act="lb">Leaderboard</button>
      <button class="btn big ghost" data-act="cloud">Cloud save</button>""")
# daily results: post score + board
rep("""    <button class="btn big brag-fb" data-act="brag" data-kind="daily">Brag about it</button>
    <button class="btn big vic-btn" data-act="dailyQuit">Back to my adventure</button></div>`);""","""    ${nameRow()}<button class="btn big" data-act="postScore" data-board="daily" data-score="${score}">Post my score</button>
    <div id="lbList"></div>
    <button class="btn big brag-fb" data-act="brag" data-kind="daily">Brag about it</button>
    <button class="btn big vic-btn" data-act="dailyQuit">Back to my adventure</button></div>`);
  api(`get-scores?board=daily&day=${D.key}`).then(j=>{ const el=$('lbList'); if(el) el.innerHTML=scoreList(j.scores,myName()); }).catch(()=>{});""")
# death: post level
rep("""<button class="btn big brag-fb" data-act="brag" data-kind="death">Challenge a friend to beat me</button>""",
    """${nameRow()}<button class="btn big" data-act="postScore" data-board="level" data-score="${(S.world||0)*1000+S.level}">Post my level to the leaderboard</button><div id="lbList"></div><button class="btn big brag-fb" data-act="brag" data-kind="death">Challenge a friend to beat me</button>""")
# auto cloud save when the player saves by hand (only if they have used cloud save)
rep("if(manual){ localStorage.setItem('aa_saved', v); toast('Game saved'); }","if(manual){ localStorage.setItem('aa_saved', v); toast('Game saved'); if(store.get('aa_cloud','')) cloudSave(true); }")
rep("    case 'dailyQuit': dailyQuit(); break;","""    case 'dailyQuit': dailyQuit(); break;
    case 'lb': lbPanel(t.dataset.board); break;
    case 'postScore': postScore(t.dataset.board, +t.dataset.score, t); break;
    case 'cloud': cloudPanel(); break;
    case 'cloudSave': cloudSave(false); break;
    case 'cloudLoad': cloudLoad(); break;
    case 'cloudCopy': { const c=prettyCode(cloudCode()); (navigator.clipboard?navigator.clipboard.writeText(c):Promise.reject()).then(()=>toast('Code copied')).catch(()=>toast(c)); break; }""")
i=s.rindex('</style>')
s=s[:i]+'''
.name-row{display:flex;flex-direction:column;gap:4px;width:100%}
.name-row label{font-family:var(--f-num);font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:var(--parch-dim)}
.name-row input{font:inherit;font-size:1.1rem;padding:10px 12px;border-radius:8px;border:3px solid #000;background:#f3e6c8;color:#16100d;box-shadow:3px 3px 0 #000}
.lb{list-style:none;margin:0;padding:0;width:100%;display:flex;flex-direction:column;gap:4px}
.lb li{display:grid;grid-template-columns:2em 1fr auto;gap:8px;align-items:center;background:#120d0b;border:2px solid #000;border-radius:8px;padding:6px 10px}
.lb li span{font-family:var(--f-num);color:var(--parch-dim)}.lb li b{font-weight:800;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.lb li em{font-style:normal;font-family:var(--f-num);font-weight:700;color:var(--gold)}
.lb li:nth-child(1) span{color:#ffd35c}.lb li.me{box-shadow:inset 0 0 0 2px var(--gold)}
.lb-tabs{width:100%}.lb-tabs .btn{flex:1;font-size:.8rem}
.cloud-code{font-family:var(--f-num);font-weight:700;font-size:clamp(1.4rem,6vw,2rem);letter-spacing:.12em;text-align:center;background:#f3e6c8;color:#16100d;border:3px solid #000;border-radius:10px;box-shadow:4px 4px 0 #000;padding:10px;user-select:all}
'''+s[i:]
open(p,'w').write(s); print('ok')
