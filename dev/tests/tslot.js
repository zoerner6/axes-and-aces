const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const [w,h,n] of [[390,844,'s1'],[462,1000,'s2'],[1440,900,'s3']]){
const p=await b.newPage({viewport:{width:w,height:h}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8765/site/audit.html');await p.evaluate(()=>{localStorage.clear();localStorage.setItem('tutorialDone','true')});await p.reload();await p.waitForTimeout(1200);
await p.evaluate(()=>window.__A.ev(`newRun(false); S.heroName='Josh'; localStorage.setItem('aa_save_1', JSON.stringify({S, at:Date.now()})); slotsPanel();`));
await p.waitForTimeout(1200); await p.screenshot({path:'/tmp/claude-0/'+n+'.png'}); console.log(n,errs);}
await b.close();})();
