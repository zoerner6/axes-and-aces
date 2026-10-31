# rebuild standing loops so the end melts into the start (no visible restart). Ping-pong ones stay as they are.
cd /tmp/claude-0/-home-user/8da1ae95-9ac9-5639-830a-e1825fc256be/scratchpad
mkdir -p vid_loopsrc
for f in vid_hd/*_idle.mp4; do m=$(basename $f _idle.mp4)
  case $m in rat|boar|goblin|imp) continue;; esac
  src=vids/${m}_idle.mp4; [ -f $src ] || src=vidsW/${m}_idle.mp4; [ -f $src ] || continue
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $src); OFF=$(python3 -c "print(round($D-1.6,3))")
  ffmpeg -v error -y -i $src -filter_complex "[0:v]fps=24,split[a][b];[a]trim=start=0.8,setpts=PTS-STARTPTS[A];[b]trim=end=0.8,setpts=PTS-STARTPTS[B];[A][B]xfade=transition=fade:duration=0.8:offset=$OFF,unsharp=5:5:0.8[o]" -map "[o]" -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -an -movflags +faststart vid_hd/${m}_idle.mp4 && \
  ffmpeg -v error -y -i vid_hd/${m}_idle.mp4 -vf scale=854:-2 -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -an -movflags +faststart vid_out/${m}_idle.mp4 && echo ok $m
done
# Quest 1 clips in the Claude preview stay full size
for m in $(ls vids/*_idle.mp4 | sed 's#vids/##;s#_idle.mp4##'); do cp vid_hd/${m}_idle.mp4 vid_out/; done
echo ALLDONE
