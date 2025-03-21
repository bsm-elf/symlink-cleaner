# Symlink Cleaner

Symlink Cleaner is a tool for managing symbolic links in a Zurg mount. It scans symlink directories, repairs broken symlinks by finding similar files in the original target directory, and removes unrepairable ones (optionally notifying Radarr/Sonarr instances). It includes a dashboard-style web UI for monitoring and configuration.

## Features
- Checks Zurg WebDAV availability before scanning.
- Repairs symlinks using the original target path (same extension).
- Removes broken symlinks and notifies Radarr/Sonarr (configurable).
- Web UI for status, config editing, and scan results.
- Runs in Docker/Kubernetes.

## Setup
1. Clone the repo: `git clone https://github.com/bsm-elf/symlink-cleaner.git`
2. Update `config.json` with your Zurg host, mount, and Radarr/Sonarr details.
3. Build and run:
   ```bash
   docker build -t symlink-cleaner .
   docker run -v ./config.json:/app/config.json -v /storage:/storage -p 5000:5000 symlink-cleaner