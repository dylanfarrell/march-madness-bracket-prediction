#\!/bin/bash
set -e

PYTHON="../.venv/bin/python"
LOG="pipeline_log.txt"

log() { echo "$(date) - $1" | tee -a "$LOG"; }

log "=== Starting pipeline ==="
log "Waiting for rate limit to clear..."
while true; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://www.sports-reference.com/cbb/schools/duke/men/2026.html")
  if [ "$STATUS" = "200" ]; then
    log "Rate limit cleared\!"
    break
  else
    log "Still rate limited ($STATUS). Retrying in 5 min..."
    sleep 300
  fi
done

log "=== Mens Data ==="
$PYTHON create_sports_reference_team_data.py --year=2026 --overwrite && log "Done: sports_ref (M)"
$PYTHON create_preseason_rankings_data.py --year=2026 --overwrite && log "Done: preseason (M)"
$PYTHON create_coaches_data.py --year=2026 --overwrite && log "Done: coaches (M)"
$PYTHON create_returning_player_team_data.py --year=2026 --overwrite && log "Done: returning_player (M)"
$PYTHON create_weighted_player_data.py --year=2026 --overwrite && log "Done: weighted_player (M)"

log "=== Womens Data ==="
$PYTHON create_sports_reference_team_data.py --year=2026 --mode=W --overwrite && log "Done: sports_ref (W)"
$PYTHON create_preseason_rankings_data.py --year=2026 --mode=W --overwrite && log "Done: preseason (W)"
$PYTHON create_coaches_data.py --year=2026 --mode=W --overwrite && log "Done: coaches (W)"

log "=== Silver Data ==="
$PYTHON create_silver_data.py --year=2026 --overwrite && log "Done: silver (M)"
$PYTHON create_silver_data.py --year=2026 --mode=W --overwrite && log "Done: silver (W)"

log "=== Gold Data ==="
$PYTHON create_gold_data.py --year=2026 --overwrite && log "Done: gold (M)"
$PYTHON create_gold_data.py --year=2026 --mode=W --overwrite && log "Done: gold (W)"

log "=== Git Push ==="
cd ..
git add data/2026/ data_engineering/
git commit -m "regenerate all 2026 data (bronze/silver/gold)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
git push
log "=== Pipeline complete ==="
