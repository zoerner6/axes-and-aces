var LVLSTEP=1.10;
var HPEXP=1.45;
/* Symmetric combat: monsters carry Attack and Defense scores for their level,
   the same way the player does, and every exchange rolls dice.

     player hit = hand x (1 + atk/100) x 1.32^(lvl-1) x aces x roll
                  / (1 + foeDefense/100)
     foe hit    = its base damage x (1 + foeAttack/100) x roll
                  / (1 + yourDefense/100)
*/
const HAND = {high:10,pair:30,two:60,trio:100,straight:150,flush:220,full:320,four:480,sflush:700};

const evalT = cs => {
  const c = {}; cs.forEach(x => c[x.r] = (c[x.r]||0)+1);
  const g = Object.values(c).sort((a,b)=>b-a);
  const fl = cs.length===5 && cs.every(x=>x.s===cs[0].s);
  const rs = cs.map(x=>x.r).sort((a,b)=>a-b);
  const st = cs.length===5 && g.length===5 && (rs[4]-rs[0]===4 || rs.join()==='0,1,2,3,12');
  if (st&&fl) return 'sflush'; if (g[0]===4) return 'four'; if (g[0]===3&&g[1]>=2) return 'full';
  if (fl) return 'flush'; if (st) return 'straight'; if (g[0]===3) return 'trio';
  if (g[0]===2&&g[1]===2) return 'two'; if (g[0]===2) return 'pair'; return 'high';
};
function best(cards){
  let bv=0,bt='high',ba=0,keep=null;
  for (let m=1;m<(1<<cards.length);m++){
    let n=0,x=m; while(x){n+=x&1;x>>=1;} if(n>5) continue;
    const sel=[]; for(let i=0;i<cards.length;i++) if(m&(1<<i)) sel.push(cards[i]);
    const t=evalT(sel); if(HAND[t]>bv){bv=HAND[t];bt=t;ba=sel.filter(c=>c.r===12).length;keep=m;}
  }
  return {t:bt,aces:ba,keep,v:bv};
}
const deck = () => {
  const d=[]; for(let s=0;s<4;s++) for(let r=0;r<13;r++) d.push({r,s});
  for(let j=d.length-1;j>0;j--){const k=Math.random()*(j+1)|0;[d[j],d[k]]=[d[k],d[j]];}
  return d;
};
/* a real player throws away what the best hand does not use, once */
function drawHand(d){
  let cards=d.splice(0,7);
  let b=best(cards);
  if (b.v < 220){
    const keep=cards.filter((c,i)=>(b.keep&(1<<i)));
    cards=keep; while(cards.length<7 && d.length) cards.push(d.pop());
    b=best(cards);
  }
  return b;
}

/* ---- the two sides ---- */
const PL_ATK = [0,0,8,16,28,48,48,75,75,110,110];      // what you'd own at each level
const PL_DEF = [0,0,40,70,120,120,190,190,280,280,280];
const myHP   = L => 400 + 100*(L-1);

// a monster's gear for its level, times how tough its kind is
const atLvl = (tbl, L) => {
  if (L <= 10) return tbl[Math.max(1, L)];
  return Math.round(tbl[10] * (1 + (L-10) * 0.06));   // past the best gear, creep slowly
};
const foeAtkScore = (L,k=1) => Math.round(atLvl(PL_ATK, L) * k);
const foeDefScore = (L,k=1) => Math.round(atLvl(PL_DEF, L) * k);
const TYPES = [0.8,0.9,0.9,1,1,1.1,1.2,1.2,1.3,1.4,1.5];

const roll = () => 0.85 + Math.random()*0.30;

function fight(pl, ml, hpBase, punch){
  const k = TYPES[(Math.random()*TYPES.length)|0];
  let hp = myHP(pl);
  let fhp = 1.27*130*Math.pow(HPEXP,ml-1)*hpBase*k;
  const myAtkMul = 1 + PL_ATK[pl]/100, lvlMul = Math.pow(LVLSTEP,pl);
  const myDefDiv = 1 + PL_DEF[pl]/100;
  const fAtkMul  = 1 + foeAtkScore(ml,k)/100;
  const fDefDiv  = 1 + foeDefScore(ml,k)/100;
  const foeBase  = Math.round((4+2.6*(ml-1))*1.25)*10*punch;
  const d = deck();
  let turns = 0;
  while (hp>0 && fhp>0 && turns<60){
    if (d.length<14) d.push(...deck());
    const b = drawHand(d);
    fhp -= (HAND[b.t] * myAtkMul * lvlMul * (1+b.aces*0.12)) / fDefDiv;
    turns++;
    if (fhp<=0) break;
    hp -= Math.max(1, (foeBase * fAtkMul * roll()) / myDefDiv);
  }
  return {won: hp>0 && fhp<=0, turns, h: Math.max(0,hp)/myHP(pl)};
}

function run(hpBase, punch, gap, label){
  console.log('');
  console.log('=== ' + label + '  (hp x' + hpBase + ', punch x' + punch + ', monster ' + gap + ' levels above you) ===');
  console.log('you  foe   win%  turns  health left');
  for (const p of [1,2,4,6,8,10]){
    const m = Math.max(1, p + gap);
    let w=0,t=0,h=0; const N=600;
    for (let i=0;i<N;i++){ const r=fight(p,m,hpBase,punch); if(r.won)w++; t+=r.turns; h+=r.h; }
    console.log(String(p).padStart(3), String(m).padStart(4),
      (w/N*100).toFixed(0).padStart(6)+'%', (t/N).toFixed(1).padStart(6), (h/N*100).toFixed(0).padStart(11)+'%');
  }
}

if (require.main === module){
  for (const [ls,e,hp,pu] of [[1.10,1.12,1.45,1.45],[1.12,1.15,1.5,1.5],[1.12,1.15,1.35,1.35]]){
    LVLSTEP=ls; HPEXP=e;
    run(hp, pu, 0, 'level x'+ls+'/lvl, monster health x'+e+'/lvl');
  }
}
module.exports = {fight, foeAtkScore, foeDefScore};
