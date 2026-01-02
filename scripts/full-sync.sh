#!/bin/bash
# Full sync: database and code to ui-box
# Usage: ./scripts/full-sync.sh
# WARNING: This overwrites the database on ui-box (including borrowing data)

set -e

cd "$(dirname "$0")/.."

echo "WARNING: This will overwrite the database on ui-box, including any borrowing data."
read -p "Are you sure? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

LIBRARY_PATH="/home/guest/library"

echo "Syncing Python scripts..."
scp src/ui.py src/search.py ui-box:$LIBRARY_PATH/

echo "Syncing database..."
scp src/db/library.db ui-box:$LIBRARY_PATH/db/

echo "Full sync complete."
