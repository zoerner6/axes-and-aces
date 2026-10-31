const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const [w,h,n] of [[1536,640,'d1'],[1280,800,'d2'],[1920,950,'d4'],[390,844,'d3']]){
const p=await b.newPage({viewport:{width:w,height:h}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8765/site/audit.html');await p.evaluate(()=>{localStorage.clear();localStorage.setItem('tutorialDone','true')});await p.reload();await p.waitForTimeout(1500);
let ok=await p.evaluate(()=>window.__A.ev(`(()=>{ try{ newRun(false); render(); S.enc='spot'; fightIntro(); return 'ok'}catch(e){return e.message} })()`));
await p.waitForTimeout(3500); await p.screenshot({path:'/tmp/claude-0/'+n+'i.png'});
let sc=await p.evaluate(()=>{const e=document.getElementById('panel');return [e.scrollHeight,e.clientHeight]});console.log(n,'intro',ok,sc);
ok=await p.evaluate(()=>window.__A.ev(`(()=>{ try{ closePanel&&closePanel(); S.trade={type:'axe',tier:0,price:6,trades:[],atk0:0,def0:0,atk1:14,def1:0}; tradePanel(); return 'ok'}catch(e){return e.message} })()`));
await p.waitForTimeout(9500); await p.screenshot({path:'/tmp/claude-0/'+n+'t.png'});
sc=await p.evaluate(()=>{const e=document.getElementById('panel');return [e.scrollHeight,e.clientHeight]});console.log(n,'trade',ok,sc,errs.slice(0,2));}
await b.close();})();
