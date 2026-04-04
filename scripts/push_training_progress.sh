#!/bin/bash
# Push training progress to GitHub for remote monitoring
# Usage: bash scripts/push_training_progress.sh [cycle_name]
#   cycle_name: cycle-1, cycle-2, cycle-3 (default: latest with active training)

set -e

CYCLE=${1:-""}

if [ -z "$CYCLE" ]; then
    # Find the cycle with the most recent metrics
    for c in cycle-3 cycle-2 cycle-1; do
        if [ -f "outputs/logs/$c/metrics.csv" ]; then
            CYCLE="$c"
            break
        fi
    done
fi

if [ -z "$CYCLE" ]; then
    echo "No training metrics found. Run training first."
    exit 1
fi

METRICS_FILE="outputs/logs/$CYCLE/metrics.csv"

if [ ! -f "$METRICS_FILE" ]; then
    echo "No metrics file for $CYCLE"
    exit 1
fi

# Get latest metrics
LATEST=$(python3 -c "
import csv
rows = list(csv.DictReader(open('$METRICS_FILE')))
if not rows:
    print('NO_DATA')
    exit()
last = rows[-1]
step = last.get('step', '?')
train_loss = last.get('train_loss', '?')
val_loss = last.get('val_loss', '?')
total = len(rows)
print(f'{step}|{train_loss}|{val_loss}|{total}')
")

if [ "$LATEST" = "NO_DATA" ]; then
    echo "No metrics data for $CYCLE"
    exit 1
fi

STEP=$(echo "$LATEST" | cut -d'|' -f1)
TRAIN_LOSS=$(echo "$LATEST" | cut -d'|' -f2)
VAL_LOSS=$(echo "$LATEST" | cut -d'|' -f3)
TOTAL_ROWS=$(echo "$LATEST" | cut -d'|' -f4)

echo "=== OCI Specialist LLM - Training Progress ==="
echo "Cycle: $CYCLE"
echo "Step: $STEP"
echo "Train Loss: $TRAIN_LOSS"
echo "Val Loss: $VAL_LOSS"
echo "Total metric points: $TOTAL_ROWS"
echo ""

# Generate a quick progress report
REPORT="outputs/logs/$CYCLE/training-progress.md"
cat > "$REPORT" << EOF
# Training Progress: $CYCLE

**Updated:** $(date -u +"%Y-%m-%d %H:%M UTC")
**Step:** $STEP
**Train Loss:** $TRAIN_LOSS
**Val Loss:** $VAL_LOSS
**Metric Points:** $TOTAL_ROWS

## Latest Metrics

| Step | Train Loss | Val Loss |
|------|-----------|----------|
| $STEP | $TRAIN_LOSS | $VAL_LOSS |

## All Metrics

\`\`\`csv
$(tail -20 "$METRICS_FILE")
\`\`\`
EOF

# Stage and commit
git add "$REPORT" "$METRICS_FILE"
git commit -m "chore: training progress $CYCLE - step $STEP, train_loss=$TRAIN_LOSS, val_loss=$VAL_LOSS" || echo "No changes to commit"

# Push
git push origin main

echo ""
echo "Training progress pushed to GitHub!"
echo "View at: https://github.com/otavio-lemos/olia-2-oci/tree/main/outputs/logs/$CYCLE"
