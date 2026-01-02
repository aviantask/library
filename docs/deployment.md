# Deploying to ui-box

The library UI runs on a separate Linux machine (ui-box) that hosts its own copy of the database. The Mac is used for development and book ingestion, with updates pushed via SSH.

## Prerequisites

- ui-box must be set up and configured (see [ui-box-setup.md](ui-box-setup.md))
- SSH key access configured from Mac to ui-box
- `~/.ssh/config` entry for ui-box (optional but recommended)

## Initial Setup (One-Time)

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
ssh ui-box 'sudo mkdir -p /home/guest/library/db && sudo chown -R guest:guest /home/guest/library'
```

### 5. Run initial deployment

```bash
./scripts/full-sync.sh
```

### 6. Set up Python environment on ui-box

```bash
ssh ui-box 'sudo -u guest bash -c "cd /home/guest/library && python3 -m venv venv && source venv/bin/activate && pip install requests beautifulsoup4"'
```

### 7. Test the UI

```bash
ssh ui-box 'sudo -u guest bash -c "cd /home/guest/library && source venv/bin/activate && python3 ui.py"'
```

## Ongoing Workflow

After making changes on your Mac, use these scripts to push updates:

### Push newly ingested books

After running `src/ingest.py` on Mac to add new books:

```bash
./scripts/push-books.sh
```

This script pushes only the database file, leaving code unchanged. Safe to run frequently.

### Deploy code changes

After modifying `ui.py`, `search.py`, or other code:

```bash
./scripts/deploy.sh
```

This script pushes code changes without touching the database.

### Full sync (use with caution)

To completely sync everything (code + database):

```bash
./scripts/full-sync.sh
```

**Warning:** This overwrites the database on ui-box. The script will ask for confirmation.

## Deploy Scripts Reference

| Script | What it does | When to use |
|--------|--------------|-------------|
| `scripts/push-books.sh` | Push database only | After ingesting new books |
| `scripts/deploy.sh` | Push code only | After modifying Python files |
| `scripts/full-sync.sh` | Push everything (with confirmation) | Initial setup or major changes |

## Troubleshooting

### Can't connect to ui-box

Check SSH connection:

```bash
ssh ui-box 'echo "Connection OK"'
```

If this fails, verify:
- ui-box is powered on and connected to network
- SSH server is running on ui-box: `systemctl status ssh`
- IP address hasn't changed (if using IP instead of hostname)

### Database not updating

After running `push-books.sh`, verify the database was copied:

```bash
ssh ui-box 'ls -lh /home/guest/library/db/library.db'
```

Check timestamp to confirm it's recent.

### UI not reflecting code changes

After running `deploy.sh`, verify files were copied:

```bash
ssh ui-box 'ls -lh /home/guest/library/ui.py'
```

If the UI is currently running, you may need to restart it (press Q to quit, it will restart on next login).

### Script permissions

If deploy scripts won't run:

```bash
chmod +x scripts/*.sh
```

## Manual Deployment

If the scripts aren't working, you can deploy manually:

### Copy database

```bash
scp src/db/library.db ui-box:/home/guest/library/db/
```

### Copy code

```bash
scp src/ui.py src/search.py ui-box:/home/guest/library/
```

### Copy entire db directory

```bash
scp -r src/db ui-box:/home/guest/library/
```

### Fix permissions after manual copy

```bash
ssh ui-box 'sudo chown -R guest:guest /home/guest/library'
```

## Network Configuration

For reliable deployment, consider:

1. **Static IP** - Configure ui-box with a static IP (see [ui-box-setup.md](ui-box-setup.md))
2. **mDNS** - Install `avahi-daemon` on ui-box to access via `ui-box.local`
3. **SSH config** - Use `~/.ssh/config` to avoid typing IP addresses

## File Locations

### On Mac (development)
- Code: `/Users/yakov/src/projects/library/src/`
- Database: `/Users/yakov/src/projects/library/src/db/library.db`
- Deploy scripts: `/Users/yakov/src/projects/library/scripts/`

### On ui-box (production)
- Everything: `/home/guest/library/`
- Database: `/home/guest/library/db/library.db`
- UI script: `/home/guest/library/ui.py`
- Virtual env: `/home/guest/library/venv/`
