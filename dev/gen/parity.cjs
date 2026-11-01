/* Josh's rule: at the same level with the same attack score, the monster and
   the hero should deal the SAME damage on average. His varies with the cards,
   the monster's varies with a dice roll around the median - and that median is
   the average points a hand is worth. Everything else is health and patterns. */
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
function drawHand(d){
  let cards=d.splice(0,7), b=best(cards);
  if(b.v<220){ const keep=cards.filter((c,i)=>(b.keep&(1<<i)));
    cards=keep; while(cards.length<7&&d.length)cards.push(d.pop()); b=best(cards); }
  return b;
}

const HP_STEP=Number(process.env.HP_STEP||1.12);
const HAND_AVG=121;          /* measured: what a played hand is worth, on average */
const LVL_STEP=1.12, ACE_MULT=.12;
const EQ={sword:[0,8,16,28,44,64],axe:[0,14,28,48,75,110],dagger:[0,4,8,14,22,32],
          shield:[0,10,20,40,60,90],helm:[0,10,20,30,50,70],armor:[0,20,30,50,80,120]};
const KIT=L=>L<=2?1:L<=4?2:L<=6?3:L<=8?4:5;
const creep=(v,L)=>L<=9?v:Math.round(v*(1+(L-9)*0.06));
const knightAtk=L=>creep(EQ.sword[KIT(L)]+EQ.dagger[KIT(L)],L);
const knightDef=L=>creep(EQ.shield[KIT(L)]+EQ.helm[KIT(L)]+EQ.armor[KIT(L)],L);
const ATK_LO=.40,ATK_HI=.95,MID_ATK=.675,MID_DEF=.5,FLOOR_DEF=5;
const temper=k=>Math.max(0,Math.min(1,((k.hp/k.atk)-0.6)/1.1));
const foeThreat=(L,b)=>(1+knightDef(L)*MID_DEF/100)*(1+knightAtk(L)*MID_ATK/100)*(b?1.3:1);
const foeAtkScore=(L,tp)=>Math.round(knightAtk(L)*(ATK_HI-(ATK_HI-ATK_LO)*tp));
const foeDefScore=(L,tp)=>Math.max(FLOOR_DEF,Math.min(knightDef(L),Math.round(100*(foeThreat(L)/(1+foeAtkScore(L,tp)/100)-1))));
/* the hero is never fully kitted: about 70% of the cap he could own */
const PL_ATK_REAL=L=>Math.round(knightAtk(L)*0.8);
const PL_DEF_REAL=L=>Math.round(knightDef(L)*0.7);
const lvlMult=L=>Math.pow(LVL_STEP,L);
/* the monster's die, mirrored from the hero's own hand spread */
const FOE_DIE=[.25,.25,.25,.5,.5,.5,.5,.833,1.25,1.833,2.667,2.667];
const roll=()=>FOE_DIE[(Math.random()*FOE_DIE.length)|0];

/* real monster patterns from the game: numbers attack, B blocks, H heals */
const PATS=[[1,1,1.6],[1,1.4],[1,1,1.5],['B',1,1.6],[0.8,0.8,2.1],[1,'H',1.4],[0.8,2],[1,1.5],[1.2,'H',1.4],[1.3,1.3],[1,'B',1.9]];
const KINDS=[0.8,0.9,0.9,1,1,1.1,1.2,1.2,1.3];   /* t.atk, the kind's own punch */
const HPK  =[0.8,0.9,1,1,1.1,1.2,1.3,1.5,1.6];   /* t.hp */

/* dealing is the slow part, so deal a big bag of hands once and draw from it */
const BAG=(()=>{ const out=[]; const d=deck();
  for(let i=0;i<40000;i++){ if(d.length<16)d.push(...deck()); const b=drawHand(d); out.push([HAND[b.t], b.aces]); }
  return out; })();
const pull=()=>BAG[(Math.random()*BAG.length)|0];

function fight(pl, ml, hpMul, myHPbase, perLvlHP){
  const ki=(Math.random()*KINDS.length)|0, ka=KINDS[ki], kh=HPK[ki];
  const pat=PATS[(Math.random()*PATS.length)|0];
  const nums=pat.filter(v=>typeof v==='number');
  const meanV=nums.reduce((a,b)=>a+b,0)/nums.length;

  const myMax=myHPbase+perLvlHP*(pl-1); let hp=myMax;
  let fhp=Math.round(130*Math.pow(HP_STEP,ml-1)*hpMul*kh);

  const myAtk=1+PL_ATK_REAL(pl)/100, myDefDiv=1+PL_DEF_REAL(pl)/100;
  const tp=temper({hp:kh,atk:ka});
  const fAtk=1+foeAtkScore(ml,tp)/100, fDefDiv=1+foeDefScore(ml,tp)/100;
  /* the monster's median hit: the same shape as the hero's, built on the same average hand */
  const foeBase=HAND_AVG*lvlMult(ml)*fAtk*ka;

  let turns=0, pot=3, step=0, block=0;
  while(hp>0&&fhp>0&&turns<80){
    const [hv,aces]=pull();
    fhp-=(hv*myAtk*lvlMult(pl)*(1+aces*ACE_MULT))/fDefDiv;
    turns++; if(fhp<=0)break;
    const mv=pat[step++%pat.length];
    if(mv==='B'){ block=Math.round(fhp*.12); }
    else if(mv==='H'){ fhp=Math.min(fhp+Math.round(fhp*.15), 130*Math.pow(HP_STEP,ml-1)*hpMul*kh); }
    else {
      let dmg=(foeBase*(mv/meanV)*roll())/myDefDiv;
      dmg=Math.max(1,dmg-block); block=0;
      hp-=dmg;
    }
    /* a player drinks when badly hurt */
    if(hp>0&&hp<myMax*0.3&&pot>0){ pot--; hp=Math.min(myMax,hp+myMax*0.35); }
  }
  return {won:hp>0&&fhp<=0, turns, h:Math.max(0,hp)/myMax};
}

function run(hpMul,myHPbase,perLvlHP,gap,label){
  console.log('\n=== '+label+' ===');
  console.log(' you  foe    win%   turns   health left');
  for(const p of [1,2,4,6,8,10]){
    const m=Math.max(1,p+gap); let w=0,t=0,h=0; const N=4000;
    for(let i=0;i<N;i++){const r=fight(p,m,hpMul,myHPbase,perLvlHP); if(r.won)w++; t+=r.turns; h+=r.h;}
    console.log(String(p).padStart(4),String(m).padStart(4),(w/N*100).toFixed(0).padStart(7)+'%',(t/N).toFixed(1).padStart(7),(h/N*100).toFixed(0).padStart(12)+'%');
  }
}
const [,,mode]=process.argv;
if(mode==='sweep'){
  for(const hpMul of [2.5,3.5,4.5,5.5]) run(hpMul,400,100,0,'monster health x'+hpMul+', hero 400+100/lvl');
} else {
  run(Number(process.argv[2]||4.5),Number(process.argv[3]||400),Number(process.argv[4]||100),Number(process.argv[5]||0),'parity');
}
