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

echo "Syncing Python scripts..."
scp src/ui.py src/search.py ui-box:~/library/

echo "Syncing database..."
scp src/db/library.db ui-box:~/library/db/

echo "Full sync complete."
