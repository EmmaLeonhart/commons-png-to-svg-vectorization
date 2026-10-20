#!/bin/sh
# One queued shadow picture, end to end: download the PNG and description into data_lake/downloads/shadow-SLUG/,
# fit with tools/shadow_rotfit.py, and if IoU >= 0.93 stage it with tools/shadow_package.py and commit. Below that,
# nothing is staged and the IoU is printed for a look.
# usage (repo root): sh tools/shadow_one.sh SLUG CODE    e.g. sh tools/shadow_one.sh hyogo 28
set -e
SLUG=$1; CODE=$2
NAME="$(echo "$SLUG" | cut -c1 | tr a-z A-Z)$(echo "$SLUG" | cut -c2-)"
T="Shadow picture of $NAME prefecture"
D="data_lake/downloads/shadow-$SLUG"
UA="agentic-vectorization/0.1 (emma@topazcomputing.com)"
mkdir -p "$D" "files/shadow-$SLUG"
[ -s "$D/$T.png" ] || curl -sfL -A "$UA" "https://commons.wikimedia.org/wiki/Special:FilePath/Shadow_picture_of_${NAME}_prefecture.png" -o "$D/$T.png"
[ -s "$D/description.wikitext" ] || curl -sf -A "$UA" "https://commons.wikimedia.org/w/index.php?title=File:Shadow_picture_of_${NAME}_prefecture.png&action=raw" -o "$D/description.wikitext"
IOU=$(python tools/shadow_rotfit.py "$SLUG" "$CODE" fit | sed -n 's/^IoU //p')
echo "$SLUG IoU $IOU"
if python -c "import sys; sys.exit(0 if float('$IOU') >= 0.93 else 1)"; then
  python tools/shadow_package.py "$SLUG" "$CODE" "$IOU"
  git add -A "files/shadow-$SLUG" "upload/shadow-$SLUG" "$D" queue.md devlog.md
  git commit -q -m "$T.png -> SVG: N03, rotation fit (IoU $IOU)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MahXmkWSoLiEgfYsCeMKSw"
  git push -q
  echo committed
else
  echo "below 0.93: not staged"
fi
