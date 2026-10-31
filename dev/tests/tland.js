const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const [w,h,n] of [[1440,900,'L'],[390,844,'P']]){
const p=await b.newPage({viewport:{width:w,height:h}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('http://localhost:8765/site/index.html');await p.waitForTimeout(2500);
await p.screenshot({path:`/tmp/claude-0/${n}0.png`});
const H=await p.evaluate(()=>document.body.scrollHeight); let i=1;
for(let y=h;y<H;y+=Math.round(h*0.9)){ await p.evaluate(y=>scrollTo(0,y),y); await p.waitForTimeout(900);
  const amb=await p.evaluate(()=>document.getElementById('amb').classList.contains('on')); const st=await p.evaluate(()=>{const r=document.getElementById('stage').getBoundingClientRect();return r.top<innerHeight*.5&&r.bottom>0});
  await p.screenshot({path:`/tmp/claude-0/${n}${i}.png`}); console.log(n,i,y,amb?'AMBUSH':'',st?'STAGE':''); i++; if(i>16)break; }
const sw=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);console.log(n,'hscroll',sw,errs.slice(0,4));
// demo
await p.evaluate(()=>document.getElementById('try').scrollIntoView()); await p.waitForTimeout(1500);
const btns=await p.$$('#hand .pc'); for(const k of [0,1,2]) await btns[k].click(); await p.waitForTimeout(300);
await p.screenshot({path:`/tmp/claude-0/${n}demo1.png`});
await p.click('#bDis'); await p.waitForTimeout(600); const b2=await p.$$('#hand .pc'); for(const k of [3,4,5,6,7]) await b2[k].click(); await p.click('#bAtk'); await p.waitForTimeout(900);
await p.screenshot({path:`/tmp/claude-0/${n}demo2.png`}); await p.waitForTimeout(2000); await p.screenshot({path:`/tmp/claude-0/${n}demo3.png`});
console.log(n,'live',await p.evaluate(()=>document.getElementById('live').textContent), errs.slice(0,4));
}
await b.close();})();
