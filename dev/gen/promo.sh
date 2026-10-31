#!/usr/bin/env bash
# Build the Facebook promo video out of clips the game already has.
# Square 1080x1080, which is what the feed shows biggest on a phone.
# Run from the repo root:  bash dev/gen/promo.sh
set -e
cd "$(dirname "$0")/../.."
OUT=dev/gen/out
mkdir -p "$OUT/clips"

SQ=1080
# bosses, in the order they appear
MONSTERS="dragon balrog kraken lich demonking"
CLIP=1.7            # seconds of each
CARD=2.6            # seconds for the opening and closing card
CARDF=65            # the same card length in frames at 25fps

# --- the opening and closing card, square, with a slow push in ---
python dev/gen/ogsquare.py

ffmpeg -v error -y -loop 1 -i "$OUT/card_square.jpg" -t $CARD \
  -vf "scale=1400:-1,zoompan=z='min(zoom+0.0006,1.10)':d=$CARDF/1:s=${SQ}x${SQ}:fps=25,format=yuv420p" \
  -c:v libx264 -preset slow -crf 20 -r 25 "$OUT/clips/00_open.mp4"

ffmpeg -v error -y -loop 1 -i "$OUT/card_end.jpg" -t $CARD \
  -vf "scale=1400:-1,zoompan=z='min(zoom+0.0005,1.08)':d=$CARDF/1:s=${SQ}x${SQ}:fps=25,format=yuv420p" \
  -c:v libx264 -preset slow -crf 20 -r 25 "$OUT/clips/99_end.mp4"

# --- each boss, centre cropped to a square ---
i=10
for m in $MONSTERS; do
  src="vid/${m}_attack.mp4"
  [ -f "$src" ] || { echo "skip $m"; continue; }
  ffmpeg -v error -y -i "$src" -t $CLIP \
    -vf "crop=ih:ih:(iw-ih)/2:0,scale=${SQ}:${SQ},fps=25,format=yuv420p,eq=saturation=1.12:contrast=1.06" \
    -an -c:v libx264 -preset slow -crf 20 -r 25 "$OUT/clips/${i}_${m}.mp4"
  i=$((i+1))
done

# --- stitch, with a quick fade between each ---
( cd "$OUT/clips" && ls *.mp4 | sort | sed "s|^|file '|; s|$|'|" > list.txt )
ffmpeg -v error -y -f concat -safe 0 -i "$OUT/clips/list.txt"  \
  -vf "fps=25,format=yuv420p" -c:v libx264 -preset slow -crf 21 -movflags +faststart \
  -an "$OUT/axes-and-aces-promo.mp4"

ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT/axes-and-aces-promo.mp4"
echo "built $OUT/axes-and-aces-promo.mp4"
