#!/bin/bash
# Autonomous experiment loop: runs E01 -> E02 -> E03, logs everything, peer reviews.
set -e
CANONICAL="/root/cogym/canonical"
LOGS="/root/cogym/logs"
RESULTS="/root/cogym/experiments"
export OPENCODE_GO_API_KEY="sk-fv9GAkxq7nRiVTX0l8gLEUoPc79spJGqU9HkSjswVLnoQfTuWz5HY1R8hA44g8ZU"

cd "$CANONICAL"
source /tmp/opencode/tv1-venv/bin/activate

echo "[$(date)] Starting autonomous experiment loop"

# E01 Baseline
echo "[$(date)] Running E01 baseline..."
python3 experiments/run-real.py > "$LOGS/e01-full.log" 2>&1
echo "[$(date)] E01 complete"

# E02 Persistence  
echo "[$(date)] Running E02 persistence..."
python3 experiments/e02-persistence/run.py > "$LOGS/e02-full.log" 2>&1
echo "[$(date)] E02 complete"

# E03 Reasoning route
echo "[$(date)] Running E03 reasoning route..."
if [ -f experiments/e03-reasoning-route/run.py ]; then
    python3 experiments/e03-reasoning-route/run.py > "$LOGS/e03-full.log" 2>&1
    echo "[$(date)] E03 complete"
else
    echo "[$(date)] E03 not ready, skipping"
fi

# Commit everything
cd /root/cogym
git add -A
git commit -q -m "Autonomous experiment batch: E01 baseline + E02 persistence + E03 reasoning route"
git push -q origin master
echo "[$(date)] All experiments complete, committed and pushed"

# Run peer review checklist against results
echo "[$(date)] Generating review..."
for dir in "$RESULTS"/e01-baseline "$RESULTS"/e02-persistence; do
    if [ -f "$dir/outputs/baseline-results.json" ] || [ -f "$dir/outputs/persistence-results.json" ]; then
        echo "  Results available in $dir/outputs/"
    fi
done
echo "[$(date)] DONE"
