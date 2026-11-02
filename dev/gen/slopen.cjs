/* Walk into Monster Solitaire the way a player does.

   The game opens on its world's story, then an intro to the first fight, and
   between fights it puts up a victory screen, sometimes a level-up, the
   merchant, and at an area boundary the path. Every harness in dev/gen needs
   to get past whichever of those is in front of it before it can touch the
   board, and a harness that clicks the board while a panel is up does not
   fail - it waits thirty seconds for an overlay that intercepts the click.

   So the doors live in one place. Add a panel to the game, add its button
   here, and every tool keeps working. */
const DOORS = ['storyNext', 'fight', 'onward', 'perk', 'leaveShop', 'quest', 'again'];

/* Press whatever is in front of you until the board is yours. Returns the
   names of the doors it went through, which is worth printing when a harness
   finds the game somewhere it did not expect. */
async function openGame(page, limit = 12) {
  const went = [];
  for (let i = 0; i < limit; i++) {
    const act = await page.evaluate(doors => {
      const o = document.getElementById('overlay');
      if (!o || o.hidden) return null;
      for (const d of doors) if (document.querySelector(`[data-act="${d}"]`)) return d;
      return 'unknown';
    }, DOORS);
    if (!act) return went;
    if (act === 'unknown') { went.push('a panel with no way out'); return went; }
    went.push(act);
    await page.click(`[data-act="${act}"]`, { timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(act === 'storyNext' ? 220 : 180);
  }
  went.push('still behind a panel after ' + limit + ' doors');
  return went;
}

module.exports = { DOORS, openGame };
