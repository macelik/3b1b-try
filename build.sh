#!/usr/bin/env bash
# Sesleri üretir (eksikse), tüm sahneleri 1080p30 render eder ve tek videoda birleştirir.
set -euo pipefail
cd "$(dirname "$0")"
QUALITY="${QUALITY:-1080p30}"
SCENES=$(python3 -c "from narration import SCENE_ORDER; print(' '.join(SCENE_ORDER))")

[ -f audio/durations.json ] || python3 tts.py

case "$QUALITY" in
  1080p30) FLAGS="--resolution 1920,1080 --frame_rate 30" ;;
  480p15)  FLAGS="-ql" ;;
  *) echo "bilinmeyen kalite: $QUALITY"; exit 1 ;;
esac
manim $FLAGS --disable_caching video.py $SCENES

mkdir -p output
LIST=$(mktemp)
for s in $SCENES; do echo "file '$PWD/media/videos/video/$QUALITY/$s.mp4'" >> "$LIST"; done
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart output/iman_ses_ve_mana.mp4
rm "$LIST"
python3 tools/make_srt.py "$QUALITY" > output/iman_ses_ve_mana.srt
echo "Hazır: output/iman_ses_ve_mana.mp4"
