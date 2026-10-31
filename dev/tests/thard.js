const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8765/site/audit.html');await p.evaluate(()=>{localStorage.clear();localStorage.setItem('aa_tutorialDone','true')});await p.reload();await p.waitForTimeout(900);
console.log(await p.evaluate(()=>window.__A.ev(`(()=>{const o=[];S.coach=-1;
for(const [i,L,tier] of [[0,1,0],[1,1,1],[5,3,2],[2,2,1],[12,6,3]]){S.level=L;S.idx=i;S.genFoe=null;S.foePick=null;S.enc=null;S.eq={main:tier?{type:'sword',tier}:null,off:null,shield:null,helm:null,armor:null};fightIntro();closePanel();startFight();
 const d=foeDef(),C=(r,s)=>cardById(cid(r,s));const pa=previewHit([C(14,0),C(14,1)]).dmg, p9=previewHit([C(9,0),C(9,1)]).dmg, fh=previewHit([C(14,0),C(14,1),C(14,2),C(9,3),C(9,2)]).dmg;
 o.push(d.name+' L'+d.lvl+' hp'+d.hp+' def'+foeArmor(d)+' | pair9:'+p9+' pairA:'+pa+' fullhouseA:'+fh+' => hits to kill w/ pairA '+Math.ceil(d.hp/pa));}
return o.join(' ## ');})()`)));
console.log(JSON.stringify(errs));await b.close();})();