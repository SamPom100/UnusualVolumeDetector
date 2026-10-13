#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Starting unusual volume scan..."

# Pull any remote changes first
git pull --rebase origin master

# Run the scanner & site generator
"$SCRIPT_DIR/venv/bin/python" website_generator.py

# Check if index.html or data changed
if git diff --quiet index.html data/alllisted.txt; then
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] No changes detected."
else
    git add index.html data/alllisted.txt
    git commit -m "chore: update daily stocks [skip ci]"
    git push origin master
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Successfully pushed updated scan to GitHub."
fi
