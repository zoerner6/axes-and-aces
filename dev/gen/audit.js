/* Screen auditor. Injected into a built page; reports what a person would
   notice: text sitting on text, pictures sliced by their frame, words cut off,
   things pushed off the edge. */
window.__AUDIT = function(label){
  const vis = el => { const s=getComputedStyle(el); if(s.display==='none'||s.visibility==='hidden'||+s.opacity===0) return false;
    const r=el.getBoundingClientRect(); return r.width>1&&r.height>1&&r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth; };
  const txt = el => (el.textContent||'').trim();
  const out = {label, viewport:innerWidth+'x'+innerHeight, overlaps:[], cropped:[], broken:[], clipped:[], offscreen:[], tiny:[]};

  /* leaf elements that actually paint text */
  const leaves=[...document.querySelectorAll('body *')].filter(el=>{
    if(!vis(el)) return false;
    if(!txt(el)) return false;
    if([...el.children].some(c=>txt(c))) return false;        // only the innermost
    return !/^(SCRIPT|STYLE|TITLE)$/.test(el.tagName);
  });
  const opaque = el => { let n=el; for(let i=0;i<4&&n;i++,n=n.parentElement){ const b=getComputedStyle(n).backgroundColor;
      if(b && !/rgba\(0, 0, 0, 0\)|transparent/.test(b)) return true; } return false; };
  for(let i=0;i<leaves.length;i++) for(let j=i+1;j<leaves.length;j++){
    const a=leaves[i], b=leaves[j];
    if(a.contains(b)||b.contains(a)) continue;
    const ra=a.getBoundingClientRect(), rb=b.getBoundingClientRect();
    const ox=Math.min(ra.right,rb.right)-Math.max(ra.left,rb.left);
    const oy=Math.min(ra.bottom,rb.bottom)-Math.max(ra.top,rb.top);
    if(ox>6 && oy>6){
      const area=ox*oy, small=Math.min(ra.width*ra.height, rb.width*rb.height);
      if(area/small>0.30 && !opaque(a) && !opaque(b))
        out.overlaps.push({a:txt(a).slice(0,42), b:txt(b).slice(0,42), cover:Math.round(area/small*100)+'%'});
    }
  }
  document.querySelectorAll('img').forEach(im=>{
    if(!vis(im)) return;
    if(im.complete && !im.naturalWidth){ out.broken.push(im.getAttribute('src')); return; }
    const fit=getComputedStyle(im).objectFit, r=im.getBoundingClientRect();
    if(fit!=='cover' || !im.naturalWidth) return;
    const k=Math.max(r.width/im.naturalWidth, r.height/im.naturalHeight);
    const cutX=1-r.width/(im.naturalWidth*k), cutY=1-r.height/(im.naturalHeight*k);
    if(Math.max(cutX,cutY)>0.22) out.cropped.push({src:(im.getAttribute('src')||'').split('/').pop(),
      box:Math.round(r.width)+'x'+Math.round(r.height), cutSides:Math.round(cutX*100)+'%', cutTopBottom:Math.round(cutY*100)+'%'});
  });
  document.querySelectorAll('.cine-scene').forEach(sc=>{
    if(!vis(sc)) return; const v=sc.querySelector('video.scene-vid');
    if(!v||!v.videoWidth) return; const r=sc.getBoundingClientRect();
    const k=Math.max(r.width/v.videoWidth, r.height/v.videoHeight);
    const cutY=1-r.height/(v.videoHeight*k), cutX=1-r.width/(v.videoWidth*k);
    if(Math.max(cutX,cutY)>0.22) out.cropped.push({src:'(scene video)', box:Math.round(r.width)+'x'+Math.round(r.height),
      cutSides:Math.round(cutX*100)+'%', cutTopBottom:Math.round(cutY*100)+'%'});
  });
  leaves.forEach(el=>{
    const s=getComputedStyle(el);
    if(/hidden|clip/.test(s.overflowY) && el.scrollHeight>el.clientHeight+3)
      out.clipped.push({t:txt(el).slice(0,46), lost:(el.scrollHeight-el.clientHeight)+'px'});
    const r=el.getBoundingClientRect();
    if(r.left<-2||r.right>innerWidth+2) out.offscreen.push({t:txt(el).slice(0,40), left:Math.round(r.left), right:Math.round(r.right)});
    if(parseFloat(s.fontSize)<10.5) out.tiny.push({t:txt(el).slice(0,40), size:s.fontSize});
  });
  out.pageScrollsSideways = document.documentElement.scrollWidth > innerWidth+2;
  return out;
};
