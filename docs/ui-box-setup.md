# Minimal Linux Setup for ui-box

This guide covers setting up a minimal terminal-only Linux installation for the library UI terminal.

## Overview

- **Distro:** Debian 12 (Bookworm) Netinst
- **Install size:** ~500MB
- **Boot time:** ~10-15 seconds to login prompt
- **Auto-login:** `guest` user, no password, launches library UI automatically

---

## Step 1: Create Installation Media

Download Debian 12 netinst:
```
https://www.debian.org/distrib/netinst
```

Choose **amd64** or **i386** depending on your laptop's architecture.

Write to USB (on Mac):
```bash
diskutil list                           # Find your USB (e.g., /dev/disk2)
diskutil unmountDisk /dev/disk2
sudo dd if=debian-12-netinst.iso of=/dev/rdisk2 bs=4m status=progress
```

---

## Step 2: Install Debian (Minimal)

Boot from USB and follow the installer:

1. Choose **"Install"** (not graphical install)
2. Set language, location, keyboard
3. **Hostname:** `ui-box`
4. **Domain:** leave blank
5. **Root password:** set something (needed for admin tasks)
6. **Create user:** `libraryadmin` (your admin account)
7. **Partitioning:** "Guided - use entire disk" is fine
8. **Software selection** - UNCHECK everything except:
   - ✅ SSH server
   - ✅ Standard system utilities
   - ❌ Debian desktop, GNOME, print server, etc.

---

## Step 3: First Boot - Install Required Packages

Login as `libraryadmin`, then:

```bash
# Become root
su -

# Update package lists
apt update

# Install minimal required packages
apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    sqlite3 \
    openssh-server \
    sudo

# Add libraryadmin to sudo group
usermod -aG sudo libraryadmin
```

---

## Step 4: Create the Guest User (No Password)

```bash
# Create guest user with no password
useradd -m -s /bin/bash guest

# Remove password requirement (empty password)
passwd -d guest
```

Do NOT add guest to sudo group - this is intentional for security.

---

## Step 5: Configure Auto-Login on TTY1

Debian uses systemd, so we override the getty service:

```bash
# Create override directory
mkdir -p /etc/systemd/system/getty@tty1.service.d

# Create autologin config
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin guest --noclear %I $TERM
EOF

# Reload systemd
systemctl daemon-reload

# Enable getty on tty1
systemctl enable getty@tty1
```

---

## Step 6: Configure Guest to Auto-Start Library UI

```bash
cat > /home/guest/.bash_profile << 'EOF'
# Auto-start library UI on login
if [ -z "$LIBRARY_STARTED" ] && [ "$(tty)" = "/dev/tty1" ]; then
    export LIBRARY_STARTED=1
    cd ~/library && source venv/bin/activate && python3 ui.py
fi
EOF

chown guest:guest /home/guest/.bash_profile
```

---

## Step 7: Set Static IP (Recommended)

For consistent SSH access:

```bash
nano /etc/network/interfaces
```

Replace DHCP config with:
```
auto eth0
iface eth0 inet static
    address 192.168.1.100    # Choose an IP outside your router's DHCP range
    netmask 255.255.255.0
    gateway 192.168.1.1      # Your router's IP
    dns-nameservers 8.8.8.8
```

Apply:
```bash
systemctl restart networking
```

---

## Step 8: Deploy the Library (from Mac)

```bash
# Set up SSH access
ssh-copy-id libraryadmin@192.168.1.100

# Add to ~/.ssh/config on Mac:
#   Host ui-box
#       HostName 192.168.1.100
#       User libraryadmin

# Create directory for guest
ssh ui-box 'sudo mkdir -p /home/guest/library && sudo chown guest:guest /home/guest/library'

# Deploy code and database
scp src/ui.py src/search.py ui-box:/home/guest/library/
scp -r src/db ui-box:/home/guest/library/

# Set up Python venv on ui-box
ssh ui-box 'sudo -u guest bash -c "cd /home/guest/library && python3 -m venv venv && source venv/bin/activate && pip install requests beautifulsoup4"'
```

---

## Step 9: Reboot and Test

```bash
ssh ui-box 'sudo reboot'
```

The system should:
1. Boot to terminal (~10-15 seconds)
2. Auto-login as `guest`
3. Automatically launch the library UI

---

## Optional Optimizations

### Reduce boot time
```bash
systemctl disable apt-daily.timer
systemctl disable apt-daily-upgrade.timer
systemctl disable man-db.timer

# Check what's slow
systemd-analyze blame
```

### Enable mDNS (access as ui-box.local)
```bash
apt install avahi-daemon
```

### Disable screen blanking
Add to `/home/guest/.bash_profile` before the UI launch:
```bash
setterm -blank 0 -powerdown 0
```

---

## User Accounts Summary

| User | Purpose | Password | Sudo |
|------|---------|----------|------|
| `root` | System admin | Yes | N/A |
| `libraryadmin` | Deploy code, SSH access | Yes | Yes |
| `guest` | Run library UI | None | No |

---

## Troubleshooting

### UI doesn't start on boot
- Check `.bash_profile` exists: `cat /home/guest/.bash_profile`
- Check ownership: `ls -la /home/guest/.bash_profile`
- Verify library files exist: `ls -la /home/guest/library/`

### Can't SSH to ui-box
- Verify IP: check router's DHCP leases or connect monitor
- Verify SSH is running: `systemctl status ssh`
- Check firewall: `iptables -L`

### Python/venv issues
- Ensure python3-venv is installed: `apt install python3-venv`
- Recreate venv: `rm -rf venv && python3 -m venv venv`

---

## Notes for Future Claude Code Sessions

If continuing this setup in a new session, key context:

1. **Project location on Mac:** `/Users/yakov/src/projects/library`
2. **Deploy scripts exist:** `scripts/push-books.sh`, `scripts/deploy.sh`, `scripts/full-sync.sh`
3. **Database:** SQLite at `src/db/library.db`, uses FTS5 for search
4. **UI:** Python curses-based terminal UI (`src/ui.py`)
5. **The library on ui-box lives at:** `/home/guest/library/`
6. **Two users on ui-box:** `libraryadmin` (admin/SSH) and `guest` (runs UI)
7. **README.md has deployment instructions** for ongoing workflow
