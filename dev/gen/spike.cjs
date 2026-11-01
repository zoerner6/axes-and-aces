/* The hero's hands span .25x to 2.667x of his average and no further: one
   source of spread. The monster has two - the kind's pattern AND the die -
   and they multiply. This measures what that costs. */
const HAND_AVG=121, LVL_STEP=1.12;
const EQ={sword:[0,8,16,28,44,64],dagger:[0,4,8,14,22,32],
          shield:[0,10,20,40,60,90],helm:[0,10,20,30,50,70],armor:[0,20,30,50,80,120]};
const KIT=L=>L<=2?1:L<=4?2:L<=6?3:L<=8?4:5;
const creep=(v,L)=>L<=9?v:Math.round(v*(1+(L-9)*0.06));
const knightAtk=L=>creep(EQ.sword[KIT(L)]+EQ.dagger[KIT(L)],L);
const knightDef=L=>creep(EQ.shield[KIT(L)]+EQ.helm[KIT(L)]+EQ.armor[KIT(L)],L);
const ATK_LO=.40,ATK_HI=.95;
const foeAtkScore=(L,tp)=>Math.round(knightAtk(L)*(ATK_HI-(ATK_HI-ATK_LO)*tp));
const PL_DEF_REAL=L=>Math.round(knightDef(L)*0.7);
const lvlMultOf=L=>Math.pow(LVL_STEP,Math.max(1,L|0));
const FOE_DIE=[.25,.25,.25,.5,.5,.5,.5,.833,1.25,1.833,2.667,2.667];
const DIE_TOP=Math.max(...FOE_DIE);
const playerHp=L=>400+100*(L-1);

/* every attack pattern in the game, and the spread each one carries */
const PATS=[[1,1.3,1],[1,1,2.2],[1,1],[.8,1.8],[1,'H',1.2],[1,'B',1.2],[.8,.8,2.2],[1,1.4],
  [1,'H',1],[1,1,1.8],[1,1,1,1.6],['H',1.2,1.5],[1,2],['B',1,1.3],[1,1.5],[1,'B',1.3],
  ['B',1,1.6],[1,'H',1.5],[1.2,'H',1.4],[1,1,2],[1,'B',1.9],[1,'H',1.9],[1,'B',2],[1,1,2.1]];
const spread=p=>{const h=p.filter(v=>typeof v==='number'); const m=h.reduce((a,b)=>a+b,0)/h.length;
  return Math.max(...h)/m;};
const BIG=Math.max(...PATS.map(spread));

/* blend the die toward 1 so pattern x die never leaves the hero's own range.
   E[face]=1, so blending keeps the mean exactly where it was. */
const squeeze=p=>Math.min(1,(DIE_TOP/p-1)/(DIE_TOP-1));

console.log('worst pattern multiplier in the game:', BIG.toFixed(2),
            '  pattern x die reaches', (BIG*DIE_TOP).toFixed(2)+'x the hero\'s average hand');
console.log('squeeze on that move:', squeeze(BIG).toFixed(3), ' -> top becomes',
            (BIG*(1+(DIE_TOP-1)*squeeze(BIG))).toFixed(2)+'x\n');
console.log('lvl  yourHP   typical hit   worst blow NOW   worst blow FIXED');
for(const L of [1,2,3,4,5,6,8,10,12]){
  const tp=.5, atk=HAND_AVG*lvlMultOf(L)*(1+foeAtkScore(L,tp)/100);
  const def=PL_DEF_REAL(L), hp=playerHp(L);
  const soft=r=>Math.round(r/(1+def/100));      /* an ordinary hit */
  const hard=r=>Math.round(r/(1+def/200));      /* a big one: armour counts half */
  const typical=soft(atk);
  const nowTop =hard(atk*BIG*DIE_TOP);
  const fixTop =hard(atk*BIG*(1+(DIE_TOP-1)*squeeze(BIG)));
  const pc=n=>(Math.round(n/hp*100)+'%').padStart(5);
  console.log(String(L).padStart(3), String(hp).padStart(8),
    (typical+pc(typical)).padStart(14),
    (nowTop+pc(nowTop)+(nowTop>=hp?' KILL':'')).padStart(17),
    (fixTop+pc(fixTop)+(fixTop>=hp?' KILL':'')).padStart(19));
}
