/* Build the monster's die straight out of the hero's own hand distribution:
   12 faces, each face the hand value at that twelfth of the real spread.
   Then the monster's roll has the same shape as the hero's cards - the same
   weak turns, the same rare big ones - not just the same average. */
const DIST=[            /* measured over 300,000 played hands, with the discard */
  ['High Card',10,2.8],['Pair',30,21.5],['Two Pair',60,36.3],['Three of a Kind',100,10.1],
  ['Straight',150,6.0],['Flush',220,5.0],['Full House',320,16.1],['Four of a Kind',480,2.2],
  ['Straight Flush',700,0.1]];
const FACES=12, faces=[];
let cum=[], run=0;
for(const [n,v,p] of DIST){ run+=p; cum.push([n,v,run]); }
for(let i=0;i<FACES;i++){
  const q=(i+0.5)/FACES*100;
  const hit=cum.find(c=>q<=c[2])||cum[cum.length-1];
  faces.push(hit[1]);
}
const mean=faces.reduce((a,b)=>a+b,0)/faces.length;
const mult=faces.map(v=>+(v/mean).toFixed(3));
const below=mult.filter(v=>v<1).length, above=mult.filter(v=>v>1).length;
console.log('faces (hand points) :', faces.join(', '));
console.log('mean of the die     :', mean.toFixed(1), ' (average played hand = 121)');
console.log('as multipliers      :', mult.join(', '));
console.log('below 1 / above 1   :', below, '/', above);
console.log('median multiplier   :', ((mult[5]+mult[6])/2).toFixed(2));
