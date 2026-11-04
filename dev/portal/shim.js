/* ================= games-portal shim =================
   One small layer between the game and whichever portal is hosting it. The
   game calls AA.* at four moments and each portal fills them in its own way.
   Both SDKs throw on any other domain, so every call is wrapped: on a plain
   web server, or with the SDK blocked, the game still plays start to finish.

   The portal measures how much the game downloads before the first
   `gameplay start`, so that call must survive the SDK still being set up.
   Anything asked for too early waits in `queued` and goes out on init. */
const AA = (function(){
  const P = '__PORTAL__';                 /* 'crazygames' | 'poki' | 'none' */
  const GAP = __AD_GAP__;                 /* milliseconds between ad breaks */
  const FREE = __AD_FREE_FIGHTS__;        /* fights before the first break */
  let ready = P === 'none', queued = [], playing = false, fights = 0, lastAd = 0;

  const cg = () => window.CrazyGames && window.CrazyGames.SDK;
  const pk = () => window.PokiSDK;
  const safe = fn => { try{ fn(); }catch(e){} };
  function send(fn){ ready ? safe(fn) : queued.push(fn); }
  function open(){ ready = true; const q = queued; queued = []; q.forEach(safe); }

  /* On CrazyGames the SDK is started before the game's own code runs, because
     the game reads its save slot the moment it starts and the data module only
     answers once the SDK is up. AABOOT did that and is holding the result, so
     there is nothing left to wait for here. */
  if(P === 'crazygames'){
    open();
  } else if(P === 'poki'){
    if(pk()) pk().init().then(open, open); else open();
  }

  /* Progress save. CrazyGames require a player's progress to live on their
     account rather than in one browser, and their data module takes the same
     four calls as localStorage, so the game's own save code is pointed here.
     Where the SDK is not up - a plain web server, a blocked SDK, Poki - this
     is localStorage, and the game saves exactly as it does on the site. */
  const cgData = () => P === 'crazygames' && window.AABOOT
                       && AABOOT.sdkReady() && cg() && cg().data;
  const store = {
    getItem(k){ try{ const d = cgData(); return d ? d.getItem(k) : localStorage.getItem(k); }catch(e){ return null; } },
    setItem(k,v){ try{ const d = cgData(); d ? d.setItem(k,v) : localStorage.setItem(k,v); }catch(e){} },
    removeItem(k){ try{ const d = cgData(); d ? d.removeItem(k) : localStorage.removeItem(k); }catch(e){} },
    clear(){ try{ const d = cgData(); d ? d.clear() : localStorage.clear(); }catch(e){} }
  };

  /* Both portals ask that the game go quiet and still while an ad plays. */
  function hush(on){
    safe(()=>{ if(typeof ac === 'undefined' || !ac) return;
      on ? ac.state === 'running' && ac.suspend() : ac.resume(); });
    document.querySelectorAll('video').forEach(v=>safe(()=>{ on ? v.pause() : v.loop && v.play().catch(()=>{}); }));
    document.documentElement.classList.toggle('ad-playing', !!on);
  }

  function loaded(){
    if(P === 'poki') send(()=>pk().gameLoadingFinished());
    if(P === 'crazygames') send(()=>cg().game.loadingStop());
  }
  function start(){
    if(playing) return; playing = true;
    if(P === 'crazygames') send(()=>cg().game.gameplayStart());
    if(P === 'poki') send(()=>pk().gameplayStart());
  }
  function stop(){
    if(!playing) return; playing = false;
    if(P === 'crazygames') send(()=>cg().game.gameplayStop());
    if(P === 'poki') send(()=>pk().gameplayStop());
  }

  /* A break between two fights: the player has finished one fight and asked
     for the next. That is the one pause both portals accept - never inside a
     hand, never on a menu button. The game must carry on whether the ad
     plays, fails to fill or is blocked, so every path ends at done(). */
  function adBreak(then){
    const done = () => { hush(false); safe(then); };
    stop();
    if(!ready || ++fights <= FREE || Date.now() - lastAd < GAP) return done();
    lastAd = Date.now();
    /* Only ask for an ad from an SDK that actually started. One that loaded
       but failed to initialize throws on the way in, and swallowing that
       would leave the game hidden until the timeout - a long look at nothing
       for a player whose SDK had a bad minute. */
    if(P === 'crazygames' && cg() && window.AABOOT && AABOOT.sdkReady()){
      let left = false;
      const fin = () => { if(left) return; left = true; done(); };
      try{ hush(true); cg().ad.requestAd('midgame', {adFinished: fin, adError: fin}); }
      catch(e){ fin(); }
      setTimeout(fin, 45000);          /* never strand the player on a stuck ad */
      return;
    }
    if(P === 'poki' && pk()){
      let left = false;
      const fin = () => { if(left) return; left = true; done(); };
      try{ pk().commercialBreak(()=>hush(true)).then(fin, fin); }
      catch(e){ fin(); }
      setTimeout(fin, 45000);
      return;
    }
    done();
  }

  /* The game runs in an iframe on a portal page: arrow keys, space and the
     wheel must move the game, never scroll the page around it. */
  addEventListener('keydown', e=>{
    if(e.target === document.body && ['ArrowDown','ArrowUp','ArrowLeft','ArrowRight',' '].includes(e.key)) e.preventDefault();
  });
  addEventListener('wheel', e=>{ if(e.target === document.body) e.preventDefault(); }, {passive:false});

  /* The portal measures how much the game downloads before the first
     `gameplay start`. Keeping the marks here lets that be checked for real
     in a browser instead of guessed from the folder size. */
  const api = {portal:P, loaded, start, stop, adBreak, store,
               marks:{boot:performance.now(), loaded:0, firstPlay:0}};
  const _loaded = api.loaded, _start = api.start;
  api.loaded = () => { if(!api.marks.loaded) api.marks.loaded = performance.now(); _loaded(); };
  api.start = () => { if(!api.marks.firstPlay) api.marks.firstPlay = performance.now(); _start(); };
  try{ window.AA = api; }catch(e){}
  return api;
})();
