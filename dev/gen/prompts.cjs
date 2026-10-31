/* Turn each scene's own story text into an image-to-video prompt. */
const {map}=require('./scenes.cjs');

const STYLE='Dark comic book illustration, heavy black ink lines, deep shadows, high contrast. '+
  'Animate the existing picture only: keep the exact original art style, colours, characters and composition. '+
  'Camera holds steady, no cuts, no new characters, no text or lettering.';

/* a little extra motion per kind of scene */
const KIND=[
  [/dragon|wyrm|drake/i,'The beast breathes, its wings and tail shift, embers drift.'],
  [/snow|frost|ice|frozen|winter/i,'Snow drifts down, breath fogs, ice glitters.'],
  [/sand|desert|dune|sun/i,'Heat shimmers, sand blows across the ground.'],
  [/sea|ship|wave|drowned|sunken|kraken|water/i,'Water rolls and laps, spray drifts, light ripples.'],
  [/marsh|bog|swamp|plague|rot/i,'Mist curls low, bubbles rise, flies drift.'],
  [/forge|mine|lava|fire|burn|flame/i,'Flames lick and flicker, sparks rise, molten light pulses.'],
  [/ghost|lich|abbey|haunt|crypt|bone|curse/i,'Ghostly light drifts, fog creeps, cloth stirs.'],
  [/storm|sky|thunder|lightning|titan/i,'Clouds churn, lightning flickers, wind whips cloth.'],
  [/abyss|demon|hell/i,'Hellfire glows and pulses, smoke coils upward.'],
  [/forest|wild|thorn|elven|tree/i,'Leaves and branches sway, light filters through, motes drift.'],
  [/tavern|pub|inn|gilded ace/i,'Firelight flickers, smoke curls, people shift slightly.'],
  [/king|hall|throne|crown|knight/i,'Banners stir, candle flames flicker, cloaks sway.'],
];
const extra = t => (KIND.find(([re])=>re.test(t))||[,'Light flickers softly and dust drifts through the air.'])[1];

function promptFor(id){
  const s=map[id];
  if(!s){
    if(id==='learn_wizard') return STYLE+' An old spellbook blazes open on a lectern, burning letters lift off the pages and swirl through the air, candle flames flicker. '+extra('fire');
    if(id==='merchant') return STYLE+' A merchant leans over his counter in a lamplit shop, weighing coins; lamp flames flicker, dust drifts, his hands and wares shift slightly.';
    return STYLE+' Subtle ambient motion.';
  }
  const plain=String(s.text).replace(/<[^>]+>/g,'').replace(/\s+/g,' ').trim();
  return `${STYLE} Scene: ${s.title}. ${plain} ${extra(s.title+' '+plain)}`;
}
module.exports={promptFor};
if(require.main===module){
  const todo=require('./out/todo.json');
  todo.slice(0,3).forEach(id=>console.log('\n['+id+']\n'+promptFor(id)));
  console.log('\n\ntotal:',todo.length);
}
