#!/bin/bash
export OPENCODE_GO_API_KEY="sk-fv9GAkxq7nRiVTX0l8gLEUoPc79spJGqU9HkSjswVLnoQfTuWz5HY1R8hA44g8ZU"
cd /root/cogym/canonical
source /tmp/opencode/tv1-venv/bin/activate
export PYTHONUNBUFFERED=1
echo "[$(date)] Waiting for E01..."
while pgrep -f "scientific-loop" > /dev/null; do sleep 30; done
echo "[$(date)] Running E02..."
python3 experiments/e02-persistence/run.py > /root/cogym/logs/e02-full.log 2>&1
echo "[$(date)] E03 dose..."
python3 experiments/e03-dose/run.py > /root/cogym/logs/e03-full.log 2>&1
echo "[$(date)] E04 social..."
python3 experiments/e04-social/run.py > /root/cogym/logs/e04-full.log 2>&1
echo "[$(date)] All done."
cd /root/cogym && git add -A && git commit -q -m "E02-E04 results" && git push -q origin master
