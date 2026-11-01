/* What a hand is actually worth, over a lot of turns.
   Deals the game's 7 cards, throws away what the best hand does not use
   (once, the way a player does), then scores the best 5. */
const {HAND, best, deck} = (()=>{
  const HAND={high:10,pair:30,two:60,trio:100,straight:150,flush:220,full:320,four:480,sflush:700};
  const evalT=cs=>{const c={};cs.forEach(x=>c[x.r]=(c[x.r]||0)+1);
    const g=Object.values(c).sort((a,b)=>b-a);
    const fl=cs.length===5&&cs.every(x=>x.s===cs[0].s);
    const rs=cs.map(x=>x.r).sort((a,b)=>a-b);
    const st=cs.length===5&&g.length===5&&(rs[4]-rs[0]===4||rs.join()==='0,1,2,3,12');
    if(st&&fl)return'sflush'; if(g[0]===4)return'four'; if(g[0]===3&&g[1]>=2)return'full';
    if(fl)return'flush'; if(st)return'straight'; if(g[0]===3)return'trio';
    if(g[0]===2&&g[1]===2)return'two'; if(g[0]===2)return'pair'; return'high';};
  const best=cards=>{let bv=0,bt='high',ba=0,keep=0;
    for(let m=1;m<(1<<cards.length);m++){let n=0,x=m;while(x){n+=x&1;x>>=1;}if(n>5)continue;
      const sel=[];for(let i=0;i<cards.length;i++)if(m&(1<<i))sel.push(cards[i]);
      const t=evalT(sel);if(HAND[t]>bv){bv=HAND[t];bt=t;ba=sel.filter(c=>c.r===12).length;keep=m;}}
    return{t:bt,aces:ba,keep,v:bv};};
  const deck=()=>{const d=[];for(let s=0;s<4;s++)for(let r=0;r<13;r++)d.push({r,s});
    for(let j=d.length-1;j>0;j--){const k=Math.random()*(j+1)|0;[d[j],d[k]]=[d[k],d[j]];}return d;};
  return {HAND,best,deck};
})();

const ACE_MULT=.12;
function run(N, discardUnder){
  const d=deck(); let count={}, sum=0, sumAce=0;
  for(let i=0;i<N;i++){
    if(d.length<16) d.push(...deck());
    let cards=d.splice(0,7), b=best(cards);
    if(b.v<discardUnder){
      const keep=cards.filter((c,j)=>(b.keep&(1<<j)));
      cards=keep; while(cards.length<7&&d.length) cards.push(d.pop());
      b=best(cards);
    }
    count[b.t]=(count[b.t]||0)+1; sum+=HAND[b.t];
    sumAce+=HAND[b.t]*(1+b.aces*ACE_MULT);
  }
  return {count, avg:sum/N, avgAce:sumAce/N};
}
const N=300000;
for(const [label,thr] of [['no discard',0],['discard unless flush+ (how a player plays)',220]]){
  const r=run(N,thr);
  console.log('\n=== '+label+' ===');
  console.log('average hand points      : '+r.avg.toFixed(1));
  console.log('average with Ace bonus   : '+r.avgAce.toFixed(1));
  const order=['high','pair','two','trio','straight','flush','full','four','sflush'];
  const names={high:'High Card',pair:'Pair',two:'Two Pair',trio:'Three of a Kind',straight:'Straight',flush:'Flush',full:'Full House',four:'Four of a Kind',sflush:'Straight Flush'};
  const pts={high:10,pair:30,two:60,trio:100,straight:150,flush:220,full:320,four:480,sflush:700};
  console.log('hand               pts     how often   share of damage');
  for(const k of order){
    const c=r.count[k]||0, pct=c/N*100;
    console.log(names[k].padEnd(18)+String(pts[k]).padStart(4)+'   '+pct.toFixed(1).padStart(8)+'%'+(pct*pts[k]/100/r.avg*100).toFixed(1).padStart(12)+'%');
  }
}
