/* Fights with the discard modelled, which the first simulation left out. */
const HAND={high:10,pair:30,two:60,trio:100,straight:150,flush:220,full:320,four:480,sflush:700};
const evalT=cs=>{const c={};cs.forEach(x=>c[x.r]=(c[x.r]||0)+1);const g=Object.values(c).sort((a,b)=>b-a);
  const fl=cs.length===5&&cs.every(x=>x.s===cs[0].s);const rs=cs.map(x=>x.r).sort((a,b)=>a-b);
  const st=cs.length===5&&g.length===5&&(rs[4]-rs[0]===4||rs.join()==='0,1,2,3,12');
  if(st&&fl)return'sflush';if(g[0]===4)return'four';if(g[0]===3&&g[1]>=2)return'full';
  if(fl)return'flush';if(st)return'straight';if(g[0]===3)return'trio';
  if(g[0]===2&&g[1]===2)return'two';if(g[0]===2)return'pair';return'high';};
function best(cards){let bv=0,bt='high',ba=0,keep=null;
  for(let m=1;m<(1<<cards.length);m++){let n=0,x=m;while(x){n+=x&1;x>>=1;}if(n>5)continue;
    const sel=[];for(let i=0;i<cards.length;i++)if(m&(1<<i))sel.push(cards[i]);
    const t=evalT(sel);if(HAND[t]>bv){bv=HAND[t];bt=t;ba=sel.filter(c=>c.r===12).length;keep=m;}}
  return {t:bt,aces:ba,keep,v:bv};}
const deck=()=>{const d=[];for(let s=0;s<4;s++)for(let r=0;r<13;r++)d.push({r,s});
  for(let j=d.length-1;j>0;j--){const k=Math.random()*(j+1)|0;[d[j],d[k]]=[d[k],d[j]];}return d;};
/* a real player throws away what the best hand does not use, once */
function drawHand(d){
  let cards=d.splice(0,8);
  let b=best(cards);
  const junk=cards.filter((c,i)=>!(b.keep&(1<<i)));
  if(junk.length && b.v<220){                      /* keep a flush or better */
    cards=cards.filter((c,i)=>(b.keep&(1<<i)));
    while(cards.length<8 && d.length) cards.push(d.pop());
    b=best(cards);
  }
  return b;
}
const TYPES=[0.8,0.9,0.9,1,1,1.1,1.2,1.2,1.3,1.4,1.5];
var EXP=1.45, BASE=1;
const monHP=(L,m)=>1.27*130*Math.pow(EXP,L-1)*BASE*m*TYPES[(Math.random()*TYPES.length)|0];
const foeHit=(L,m)=>Math.round((4+2.6*(L-1))*1.25)*10*1.5*m;  /* FOE_PUNCH 1.5 */
const foeArm=L=>Math.max(5,Math.round((5+6.5*(L-1))/5)*5);
const myHP=L=>400+100*(L-1);
const ATK=[0,0,8,16,28,48,48,75,75,110,110], DEF=[0,0,40,70,120,120,190,190,280,280,280];
function fight(pl,ml,hpM,atkM){
  let hp=myHP(pl), fhp=monHP(ml,hpM), t=0;
  const aM=1+ATK[pl]/100, lM=Math.pow(1.32,pl-1), dD=1+DEF[pl]/100, ar=1+foeArm(ml)/100;
  const d=deck();
  while(hp>0&&fhp>0&&t<40){
    if(d.length<16) d.push(...deck());
    const b=drawHand(d);
    fhp-=Math.floor(HAND[b.t]*aM*lM*(1+b.aces*0.12))/ar; t++;
    if(fhp<=0) break;
    hp-=Math.max(1,Math.round(foeHit(ml,atkM)/dD));
  }
  return {won:hp>0&&fhp<=0,t,h:Math.max(0,hp)/myHP(pl)};
}
function run(hpM,atkM,label){
  console.log('\n--- '+label+'  (monster HP x'+hpM+', damage x'+atkM+') ---');
  console.log('you  foe  win%  turns  health left');
  for(const [p,m] of [[1,1],[2,3],[4,6],[5,6],[7,8],[10,11]]){
    let w=0,tt=0,h=0;const N=600;
    for(let i=0;i<N;i++){const r=fight(p,m,hpM,atkM); if(r.won)w++; tt+=r.t; h+=r.h;}
    console.log(String(p).padStart(3),String(m).padStart(4),(w/N*100).toFixed(0).padStart(5)+'%',
      (tt/N).toFixed(1).padStart(6),(h/N*100).toFixed(0).padStart(11)+'%');
  }
}



var CASES=[[2,3,'2 under'],[4,6,'2 under'],[6,7,'1 under'],[6,6,'on level'],[8,9,'1 under'],[8,8,'on level'],[10,10,'on level']];
function spread(exp,base,label){
  EXP=exp; BASE=base;
  console.log('');
  console.log('=== exponent '+exp+'  base x'+base+'  '+label+' ===');
  console.log('you  foe  gap        win%  turns  health');
  for(var i=0;i<CASES.length;i++){
    var p=CASES[i][0],m=CASES[i][1],g=CASES[i][2];
    var w=0,t=0,h=0,N=700;
    for(var j=0;j<N;j++){var r=fight(p,m,1,1); if(r.won)w++; t+=r.t; h+=r.h;}
    console.log(String(p).padStart(3),String(m).padStart(4),' '+g.padEnd(10),(w/N*100).toFixed(0).padStart(4)+'%',(t/N).toFixed(1).padStart(6),(h/N*100).toFixed(0).padStart(8)+'%');
  }
}
spread(1.45,1.35,'as published');
spread(1.34,2.6,'flatter curve, tougher baseline');
spread(1.30,3.2,'flatter still');
