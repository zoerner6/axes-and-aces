/* Where the board is, whichever board it is.

   Every sl* tool was written against Tri-Peaks and reaches into it directly -
   `.peaks .pk.free` for a card you can play, `R.tableau` for the cards,
   `[data-act="turn"]` for the deck. Klondike has none of those, so six of the
   ten tools did not report a problem, they threw. One of them, slperks, threw
   AFTER printing two real findings, which is the worst of both.

   So the parts that differ live here, once, keyed by board. A tool asks for
   the board's selectors and gets the right ones; a third board would mean one
   entry rather than ten edits. */

const SEL = {
  peaks: {
    box:      '.peaks',
    cards:    '.peaks .pk',
    playable: '.peaks .pk.free',
    draw:     '[data-act="turn"]',
  },
  klondike: {
    box:      '.kl-cols',
    cards:    '.kl-col > .pk, .kl-top .pk',
    playable: '.pk.kl.live, [data-from="w"].live',
    draw:     '[data-act="draw"]',
  },
};

/* Run inside the page: what the board holds, in a shape both boards can
   answer. Tools that only want a count or a signature should ask this rather
   than reaching for R themselves. */
const READ = {
  peaks: `(() => {
    const R = window.__SOL.R;
    const card = c => c ? '\${c.r}\${c.s}' : '-';
    return { kind:'peaks',
             cards: R.tableau.length,
             left: R.tableau.filter(c => !c.gone).length,
             stock: R.stock.length - R.si,
             sig: R.tableau.map(c => c.r + '/' + c.s).join(',') + '|' + R.stock.map(c => c.r + '/' + c.s).join(',') };
  })()`,
  klondike: `(() => {
    const R = window.__SOL.R;
    return { kind:'klondike',
             cards: R.cols.reduce((a, c) => a + c.down.length + c.up.length, 0),
             left: R.cols.reduce((a, c) => a + c.down.length + c.up.length, 0),
             stock: R.stock.length,
             sig: R.cols.map(c => c.down.concat(c.up).map(x => x.r + '/' + x.s).join('.')).join(',')
                  + '|' + R.stock.map(c => c.r + '/' + c.s).join(',') };
  })()`,
};

/* Make the board have no legal move, so a tool can test what the game does
   when a player is stuck. Each board gets there its own way: Tri-Peaks by
   making every card the same rank as nothing on the pile, Klondike by taking
   the whole tableau down to cards that cannot stack and cannot go home. */
const DEADEN = {
  peaks: `(() => {
    const R = window.__SOL.R;
    R.tableau.forEach(c => { if(!c.gone) c.r = 7; });
    R.pile = { r: 1, s: 0 };
    window.__SOL.render();
    return window.__SOL.anyLegal();
  })()`,
  klondike: `(() => {
    const R = window.__SOL.R;
    /* every face-up card a black seven: a black seven cannot sit on another
       black seven, and with no ace home none of them can go home either */
    R.cols.forEach(col => { col.down = []; col.up = [{ r: 7, s: 0 }]; });
    R.found = [0, 0, 0, 0];
    R.waste = [];
    window.__SOL.render();
    return window.__SOL.anyLegal();
  })()`,
};

module.exports = {
  /* the board a page is currently on, asked of the page itself */
  kindScript: `(window.__SOL && window.__SOL.R && window.__SOL.R.kind) || 'peaks'`,
  sel: k => SEL[k] || SEL.klondike,
  readScript: k => READ[k] || READ.klondike,
  deadenScript: k => DEADEN[k] || DEADEN.klondike,
  boards: Object.keys(SEL),
};
