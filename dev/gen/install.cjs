/* Take generated clips from a drop folder and install them as vid/sc_<id>.mp4,
   stripped of audio and compressed so the site stays light. */
const fs=require('fs'), path=require('path'), cp=require('child_process');
const root=path.join(__dirname,'..','..');
const drop=process.argv[2]||path.join(__dirname,'out','drop');
if(!fs.existsSync(drop)){ console.error('no drop folder:',drop); process.exit(1); }
let done=0, bytesIn=0, bytesOut=0;
for(const f of fs.readdirSync(drop).filter(f=>f.endsWith('.mp4'))){
  const id=f.replace(/\.mp4$/,'');
  const src=path.join(drop,f), dst=path.join(root,'vid','sc_'+id+'.mp4');
  bytesIn+=fs.statSync(src).size;
  try{
    cp.execFileSync('ffmpeg',['-v','error','-y','-i',src,'-an',
      '-c:v','libx264','-preset','slow','-crf','27','-pix_fmt','yuv420p',
      '-vf','scale=1280:-2','-movflags','+faststart',dst],{stdio:'pipe'});
    bytesOut+=fs.statSync(dst).size; done++;
    console.log('installed sc_'+id+'.mp4', (fs.statSync(dst).size/1048576).toFixed(2)+'MB');
  }catch(e){ console.error('FAILED',id, String(e.message).slice(0,120)); }
}
console.log('\ninstalled',done,'clips  '+(bytesIn/1048576).toFixed(0)+'MB -> '+(bytesOut/1048576).toFixed(0)+'MB');
