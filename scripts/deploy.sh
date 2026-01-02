#!/bin/bash
# Deploy code changes to ui-box
# Usage: ./scripts/deploy.sh

set -e

cd "$(dirname "$0")/.."

LIBRARY_PATH="/home/guest/library"

echo "Deploying Python scripts to ui-box..."
scp src/ui.py src/search.py ui-box:$LIBRARY_PATH/

echo "Code deployed to ui-box successfully."
