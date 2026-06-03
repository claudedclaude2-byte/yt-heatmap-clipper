#!/usr/bin/env bash
# Daily AI Video Runner
# Usage: bash run_daily_video.sh
# Creates one vertical 9:16 MP4 per day in daily_ai_videos/YYYY-MM-DD/

set -e
DATE=$(date +%Y-%m-%d)
DIR="daily_ai_videos/$DATE"
mkdir -p "$DIR"

echo "=== Daily AI Video: $DATE ==="
echo "Output dir: $DIR"

python3 "$DIR/generate_video.py"

echo ""
echo "=== Deliverables ==="
ls -lh "$DIR/"
echo ""
echo "Final video: $DIR/final_video.mp4"
