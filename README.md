# Library

A personal library management system for cataloging physical books, searching the collection, and tracking borrowers. Designed with a retro green-screen terminal UI for a dedicated Linux machine.

## Features

- **ISBN-based ingestion** - Add books by ISBN, automatically fetch metadata from OpenLibrary
- **Full-text search** - Search by title, author, subject, or publication year with fuzzy matching
- **Terminal UI** - Retro green-screen interface for browsing and searching the catalog
- **Borrower tracking** - Track who borrowed what and when (planned)
- **Multi-machine deployment** - Develop on Mac, deploy to dedicated Linux terminal

## Quick Start

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Ingesting Books

Add ISBNs to `src/data/isbn.txt` (one per line), then run:

```bash
python3 src/ingest.py
```

Book data is saved to the SQLite database at `src/db/library.db`.

### Searching

Search from the command line:

```bash
python3 src/search.py title "tale"
python3 src/search.py author "orwell"
python3 src/search.py subject "science"
python3 src/search.py year 2013
```

Pipe to `less` for large result sets:

```bash
python3 src/search.py subject "fiction" | less
```

### Terminal UI

Launch the interactive catalog browser:

```bash
python3 src/ui.py
```

**Controls:**
- `↑/↓` - Navigate menu / scroll results
- `u/d` - Scroll by half-page
- `PgUp/PgDn` - Scroll by full page
- `Enter` - Select option
- `Esc` - Cancel input
- `Q` - Quit / return to menu

## Architecture

The system has two main components:

**Ingestion Pipeline** - Runs on your development machine (Mac). Looks up book metadata via OpenLibrary API, scrapes additional details like Dewey Decimal classification, and stores everything in a SQLite database with full-text search.

**UI Terminal** - Runs on a dedicated Linux box (`ui-box`) configured with auto-login to a `guest` user that launches the library UI on boot. Think library catalog terminal at your local library, but at home.

See [CLAUDE.md](CLAUDE.md) for detailed architecture and component descriptions.

## Deployment

The library is designed to run on a separate Linux machine (`ui-box`) that boots directly into the catalog interface.

For deployment instructions:
- **Initial setup**: See [docs/ui-box-setup.md](docs/ui-box-setup.md) for setting up the Linux machine
- **Ongoing deployment**: See [docs/deployment.md](docs/deployment.md) for pushing updates and new books

## Development

This is a Python codebase following two principles:
1. **Clarity above all else**
2. **After clarity, simplicity above all else**

No fancy abstractions. No over-engineering. Just straightforward, readable code.
