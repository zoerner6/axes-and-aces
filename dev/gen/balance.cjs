/* Simulate real fights: real card draws, real hand picking, real formulas. */
const HAND={high:10,pair:30,two:60,trio:100,straight:150,flush:220,full:320,four:480,sflush:700};
const evalT=cs=>{const cnt={};cs.forEach(c=>cnt[c.r]=(cnt[c.r]||0)+1);const g=Object.values(cnt).sort((a,b)=>b-a);
  const flush=cs.length===5&&cs.every(c=>c.s===cs[0].s);const rs=cs.map(c=>c.r).sort((a,b)=>a-b);
  const straight=cs.length===5&&g.length===5&&(rs[4]-rs[0]===4||rs.join()==='0,1,2,3,12');
  if(straight&&flush)return'sflush';if(g[0]===4)return'four';if(g[0]===3&&g[1]>=2)return'full';
  if(flush)return'flush';if(straight)return'straight';if(g[0]===3)return'trio';
  if(g[0]===2&&g[1]===2)return'two';if(g[0]===2)return'pair';return'high';};
function bestOf(cards){let bv=0,bt='high',aces=0;const n=cards.length;
  for(let m=1;m<(1<<n);m++){let c=0,x=m;while(x){c+=x&1;x>>=1;}if(c>5)continue;
    const sel=[];for(let i=0;i<n;i++)if(m&(1<<i))sel.push(cards[i]);
    const t=evalT(sel);if(HAND[t]>bv){bv=HAND[t];bt=t;aces=sel.filter(c=>c.r===12).length;}}
  return {t:bt,aces};}
const shuffle=()=>{const d=[];for(let s=0;s<4;s++)for(let r=0;r<13;r++)d.push({r,s});
  for(let j=d.length-1;j>0;j--){const k=Math.random()*(j+1)|0;[d[j],d[k]]=[d[k],d[j]];}return d;};

const monHP=(L,hpMul)=>1.27*130*Math.pow(1.45,L-1)*hpMul;
const foeHit=(L,atkMul)=>Math.round((4+2.6*(L-1))*1.25)*10*atkMul;
const foeArm=L=>Math.max(5,Math.round((5+6.5*(L-1))/5)*5);
const myHP=L=>400+100*(L-1);
const ATK=[0,0,8,16,28,28,48,48,75,75,110], DEF=[0,0,40,70,120,120,190,190,280,280,280];

function fight(pl,ml,hpMul,atkMul){
  let hp=myHP(pl), fhp=monHP(ml,hpMul), turns=0;
  const aM=1+ATK[pl]/100, lM=Math.pow(1.32,pl-1), dDiv=1+DEF[pl]/100, arm=1+foeArm(ml)/100;
  while(hp>0&&fhp>0&&turns<40){
    const d=shuffle(); const b=bestOf(d.slice(0,8));
    const dmg=Math.floor(HAND[b.t]*aM*lM*(1+b.aces*0.12))/arm;
    fhp-=dmg; turns++;
    if(fhp<=0) break;
    hp-=Math.max(1,Math.round(foeHit(ml,atkMul)/dDiv));
  }
  return {won:hp>0&&fhp<=0, turns, hpLeft:Math.max(0,hp)/myHP(pl)};
}
function run(hpMul,atkMul,label){
  console.log('\n=== '+label+'  (monster HP x'+hpMul+', monster damage x'+atkMul+') ===');
  console.log('you  foe  win%   turns  health left');
  for(const [pl,ml] of [[1,1],[2,3],[3,4],[5,6],[7,8],[10,10]]){
    let w=0,t=0,h=0;const N=500;
    for(let i=0;i<N;i++){const r=fight(pl,ml,hpMul,atkMul); if(r.won)w++; t+=r.turns; h+=r.hpLeft;}
    console.log(String(pl).padStart(3), String(ml).padStart(4), (w/N*100).toFixed(0).padStart(5)+'%',
      (t/N).toFixed(1).padStart(7), (h/N*100).toFixed(0).padStart(11)+'%');
  }
}
run(1,1,'NOW');
for(const am of [1.3,1.5,1.6,1.7]) run(1,am,'damage x'+am);
