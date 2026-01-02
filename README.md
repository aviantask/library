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

# Deploying to ui-box

The library UI runs on a separate Linux machine (ui-box) that hosts its own copy of the database. The Mac is used for development and book ingestion, with updates pushed via SSH.

## Initial Setup (one-time)

### 1. Install SSH server on ui-box
```bash
# On ui-box
sudo apt install openssh-server
```

### 2. Set up SSH key access from Mac
```bash
# On Mac - generate key if needed
ssh-keygen -t ed25519 -C "library-deploy"

# Copy key to ui-box
ssh-copy-id libraryadmin@<ui-box-ip>
```

### 3. Add SSH config for convenience
Add to `~/.ssh/config` on Mac:
```
Host ui-box
    HostName <ui-box-ip-or-hostname>
    User libraryadmin
```

### 4. Create directory structure on ui-box
```bash
ssh ui-box 'mkdir -p ~/library/db'
```

### 5. Run initial deployment
```bash
./scripts/full-sync.sh
```

### 6. Set up Python environment on ui-box
```bash
ssh ui-box 'cd ~/library && python3 -m venv venv && source venv/bin/activate && pip install requests beautifulsoup4'
```

### 7. Test the UI
```bash
ssh ui-box 'cd ~/library && source venv/bin/activate && python3 ui.py'
```

## Ongoing Workflow

After ingesting new books on Mac:
```bash
./scripts/push-books.sh
```

After changing code on Mac:
```bash
./scripts/deploy.sh
```

## Deploy Scripts

| Script | Purpose |
|--------|---------|
| `scripts/push-books.sh` | Push newly ingested books (additive, safe) |
| `scripts/deploy.sh` | Deploy code changes (ui.py, search.py) |
| `scripts/full-sync.sh` | Full sync with confirmation (overwrites DB)
