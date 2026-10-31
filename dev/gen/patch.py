import sys
p=sys.argv[1]; s=open(p).read()
def R(a,b):
    global s
    assert s.count(a)==1, (s.count(a), a[:80])
    s=s.replace(a,b)

# --- CSS ---
R('''.stage{position:relative;flex:1 1 auto;min-height:112px;max-height:400px;border-radius:16px;overflow:hidden;border:1px solid var(--line);display:flex;flex-direction:column;background:var(--scene)}''',
'''.stage{position:relative;flex:1 1 auto;min-height:112px;max-height:400px;border-radius:16px;overflow:hidden;border:3px solid #000;display:flex;flex-direction:column;
  background:linear-gradient(rgba(10,5,3,.55), rgba(10,5,3,.05) 38%, rgba(10,5,3,.05) 70%, rgba(10,5,3,.6)), var(--bgimg) center/cover no-repeat, var(--scene)}
.stage[data-area="0"]{--bgimg:url(art/bg_tavern.webp)} .stage[data-area="1"]{--bgimg:url(art/bg_cellar.webp)}
.stage[data-area="2"]{--bgimg:url(art/bg_forest.webp)} .stage[data-area="3"]{--bgimg:url(art/bg_castle.webp)}''')
R('''.foe-icon{flex:1;display:grid;place-items:center;''','''.foe-icon{flex:1;min-height:0;display:grid;place-items:center;''')
R('''@keyframes breathe{''','''.foe-icon img{display:block;height:clamp(96px,26vh,290px);max-width:78%;object-fit:contain}
.fc-ic img{display:block;width:88px;height:88px;object-fit:contain}
.vic-foe .vf img{display:block;height:110px;width:auto}
.story-art{width:100%;aspect-ratio:16/7;border-radius:12px;border:3px solid #000;background:center/cover no-repeat;display:grid;place-items:end start;padding:8px;box-sizing:border-box;font-size:2.6rem;line-height:1;max-width:100%}
.story-art span{filter:drop-shadow(0 3px 4px rgba(0,0,0,.8))}
@keyframes breathe{''')
R('''  background:var(--card);border:1px solid var(--card-edge);border-radius:7px;padding:0;position:relative;color:var(--ink);''',
'''  background:url(art/card_face.webp) center/100% 100% no-repeat, var(--card);border:2px solid #1a1110;border-radius:7px;padding:0;position:relative;color:var(--ink);overflow:visible;''')
R('''.card .md.face{font-family:var(--f-title)}''','''.card .md.face{font-family:var(--f-title);width:100%;margin-top:18%}
.card .md.face img{display:block;width:74%;margin:0 auto;border-radius:4px;border:1.5px solid #1a1110}''')
R('''.mini-sold svg{width:100%;height:100%;max-height:96px;display:block}''','''.mini-sold svg{width:100%;height:100%;max-height:96px;display:block}
.mini-sold img{display:block;height:96px;width:auto;max-width:100%;margin:0 auto;object-fit:contain}
.sold-fig img.soldier-svg{display:block;width:auto;height:240px;max-width:100%;margin:0 auto;object-fit:contain}
@media (max-width:700px){ .split-side .sold-fig img.soldier-svg{height:170px} }''')

# --- art lookup ---
R('''function genMonster(a, L, fixed){''','''/* dark comic art: one picture per monster, by name */
const ART = {'Sneaky Goblin':'goblin','Giant Rat':'rat','Tavern Bat':'bat','Wild Boar':'boar','Little Imp':'imp','Bandit Chief':'bandit',
  'Rattling Skeleton':'skeleton','Giant Spider':'spider','Cellar Snake':'snake','Lost Zombie':'zombie','Giant Scorpion':'scorpion','Cellar Ghoul':'ghoul',
  'Dire Wolf':'wolf','Wolf Pack':'wolf','Swamp Witch':'witch','Angry Bear':'bear','Treant':'treant','Giant Toad':'toad','Troll King':'troll',
  'Dark Knight':'knight','Stone Gargoyle':'gargoyle','Castle Ghost':'ghost','Vampire':'vampire','Baby Dragon':'babydragon','Grimstone Dragon':'dragon'};
const foeArt = (name, icon) => ART[name] ? `<img src="art/${ART[name]}.webp" alt="${name}" draggable="false">` : icon;
const BG = ['tavern','cellar','forest','castle'];
function genMonster(a, L, fixed){''')
R('''$('foeIcon').textContent = d.icon;''','''if($('foeIcon').dataset.name!==d.name){ $('foeIcon').innerHTML = foeArt(d.name, d.icon); $('foeIcon').dataset.name=d.name; }''')
R('''<div class="fc-ic">${d.icon}</div>''','''<div class="fc-ic">${foeArt(d.name, d.icon)}</div>''')
R('''<span class="vf">${w.icon}</span>''','''<span class="vf">${foeArt(w.name, w.icon)}</span>''')
# cards: J Q K portraits
R('''<span class="md ${face?'face':''}">${face?RL(c.rank):s.s}</span>''','''<span class="md ${face?'face':''}">${face?`<img src="art/face_${RL(c.rank).toLowerCase()}.webp" alt="" draggable="false">`:s.s}</span>''')
# hero picture: looks tougher as armor gets better
i=s.index('function soldierSVG(){'); j=s.index('function soldierCard(){')
s=s[:i]+'''function soldierSVG(){
  const t=Math.max(0,...['armor','helm','shield'].map(k=>S.eq[k]?S.eq[k].tier:0));
  return `<img class="soldier-svg" src="art/hero_t${t}.webp" alt="Your soldier" draggable="false">`;
}
'''+s[j:]
# story pages get a scene picture
R('''  openPanel(`<div class="story"><div class="big-icon">${pg.icon}</div></div>''','''  const scene = {start:0,a1:1,a2:2,a3:3,end:S.story.page===2?0:3}[S.story.key];
  openPanel(`<div class="story-art" style="background-image:url(art/bg_${BG[scene]}.webp)"><span>${pg.icon}</span></div>''')
# keep the art from re-rendering on every render() is handled by dataset.name; reset on new fight icon class
open(p,'w').write(s); print('ok')
