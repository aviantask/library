#!/bin/bash
# Push newly ingested books to ui-box
# Usage: ./scripts/push-books.sh

set -e

cd "$(dirname "$0")/.."

if [ ! -f "src/data/output.json" ]; then
    echo "Error: src/data/output.json not found. Run ingestion first."
    exit 1
fi

LIBRARY_PATH="/home/guest/library"

echo "Generating SQL from output.json..."
python3 src/db/json_to_sql.py src/data/output.json | ssh ui-box "sqlite3 $LIBRARY_PATH/db/library.db"

echo "Books pushed to ui-box successfully."
