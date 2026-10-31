# encode standing loops sharp at full 720p: encidle.sh SRCDIR slug...
S=$1; shift
for m in "$@"; do f=$S/${m}_idle.mp4; [ -f $f ] || continue
  case $m in rat|boar|goblin|imp) FC="[0:v]split[a][b];[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1,unsharp=5:5:0.8[o]";; *) D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f); OFF=$(python3 -c "print(round($D-1.6,3))"); FC="[0:v]fps=24,split[a][b];[a]trim=start=0.8,setpts=PTS-STARTPTS[A];[b]trim=end=0.8,setpts=PTS-STARTPTS[B];[A][B]xfade=transition=fade:duration=0.8:offset=$OFF,unsharp=5:5:0.8[o]";; esac
  ffmpeg -v error -y -i $f -filter_complex "$FC" -map "[o]" -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -an -movflags +faststart ${OUT:-vid_out}/${m}_idle.mp4
done
