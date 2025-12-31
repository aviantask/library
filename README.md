# Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

# Usage

Add ISBNs to `src/data/isbn.txt` (one per line), then run:

```bash
python3 src/ingest.py
```

Output will be written to `src/example-output.json`.
