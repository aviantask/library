#!/bin/bash
# Deploy code changes to ui-box
# Usage: ./scripts/deploy.sh

set -e

cd "$(dirname "$0")/.."

echo "Deploying Python scripts to ui-box..."
scp src/ui.py src/search.py ui-box:~/library/

echo "Code deployed to ui-box successfully."
