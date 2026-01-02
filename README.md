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

## Search

Search the library by title, author, subject, or year:

```bash
python3 src/search.py title "tale"
python3 src/search.py author "orwell"
python3 src/search.py subject "science"
python3 src/search.py year 2013
```

Pipe to `less` for paging large result sets:

```bash
python3 src/search.py subject "fiction" | less
```

## Terminal UI

Launch the interactive catalog browser:

```bash
python3 src/ui.py
```

Controls:
- `↑/↓` - Navigate menu / scroll results
- `u/d` - Scroll results by half-page
- `PgUp/PgDn` - Scroll results by full page
- `Enter` - Select option
- `Esc` - Cancel input
- `Q` - Quit / return to menu
