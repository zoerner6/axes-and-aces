/* Axes & Aces Monsters - builds a compendium of the 168 creatures.
 *
 * Foundry pack formats change between major versions, so rather than ship a
 * prebuilt pack this imports from bundled JSON into a world compendium. Run
 * it once; after that the compendium is yours.
 */
const MODULE = "axes-and-aces-monsters";
const PACK_LABEL = "Axes & Aces Monsters";

async function importMonsters() {
  const res = await fetch(`modules/${MODULE}/data/monsters.json`);
  if (!res.ok) return ui.notifications.error("Axes & Aces: monsters.json is missing.");
  const monsters = await res.json();

  let pack = game.packs.find(p => p.metadata.label === PACK_LABEL
                                  && p.metadata.packageType === "world");
  if (!pack) {
    pack = await CompendiumCollection.createCompendium({
      label: PACK_LABEL, type: "Actor", packageType: "world"
    });
  }

  ui.notifications.info(`Axes & Aces: importing ${monsters.length} monsters...`);
  const existing = new Set((await pack.getIndex()).map(e => e.name));
  const batch = monsters.filter(m => !existing.has(m.name));
  for (const m of batch) {
    const data = foundry.utils.deepClone(m);
    delete data._id;
    await Actor.create(data, { pack: pack.collection, keepId: false });
  }
  ui.notifications.info(`Axes & Aces: ${batch.length} monsters imported into "${PACK_LABEL}".`);
}

Hooks.once("init", () => {
  game.settings.registerMenu(MODULE, "import", {
    name: "Import the monsters",
    label: "Import 168 monsters",
    hint: "Builds a world compendium holding every creature from the book.",
    icon: "fas fa-dragon",
    type: class extends FormApplication {
      render() { importMonsters(); return this; }
    },
    restricted: true
  });
});

Hooks.once("ready", () => {
  if (!game.user.isGM) return;
  game.modules.get(MODULE).api = { importMonsters };
  console.log("Axes & Aces Monsters | ready. "
    + "Run game.modules.get('axes-and-aces-monsters').api.importMonsters() "
    + "or use the module settings button.");
});
