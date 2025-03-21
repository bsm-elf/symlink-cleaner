# Symlink Cleaner

Symlink Cleaner is a Python-based utility crafted to maintain symbolic links in a Zurg-powered media ecosystem. It’s designed for users managing extensive media libraries with tools like Radarr and Sonarr, where symlinks can break due to file changes in the Zurg mount (e.g., Real-Debrid or similar). The app scans user-defined directories, repairs broken symlinks by finding matching files with the same extension in the original target directory, and optionally removes unrepairable links while notifying Radarr and Sonarr instances to refresh their metadata. With a sleek, Bootstrap-based web UI, real-time updates via WebSockets, and flexible configuration (UI, `config.json`, or env vars), it supports both on-demand and scheduled scans. Docker-ready, it’s perfect for automated media management workflows.

## Description
In media setups using Zurg, symlinks often break when files in the mount (e.g., `/storage/realdebrid-zurg/__all__`) are renamed or replaced. Symlink Cleaner fixes this by:
- Checking Zurg’s WebDAV availability.
- Repairing symlinks to valid targets.
- Removing dead links and syncing with Radarr/Sonarr (optional).
It’s particularly useful in setups where files in Zurg’s mount (e.g., `/storage/realdebrid-zurg/__all__`) are updated or replaced, breaking symlinks in directories like `/storage/symlinks/movies`. The app checks Zurg’s availability before scanning, repairs symlinks where possible, and cleans up dead links, optionally syncing changes with Radarr and Sonarr via API calls. Whether you’re running a home media server or a complex Dockerized setup, Symlink Cleaner keeps your library tidy and accessible.

### Components
- **Backend (`symlink_cleaner.py`)**:
  - Flask app with SocketIO for real-time UI updates.
  - Core logic for scanning, repairing, and removing symlinks.
  - Integration with Zurg (WebDAV checks) and Arr instances (API notifications).
  - Scheduling via the `schedule` library for automated runs.
- **Frontend (`templates/index.html`)**:
  - Responsive Bootstrap UI with a dashboard layout.
  - Real-time Zurg status, scan results, and a configuration form.
  - Dynamic fields for adding Radarr/Sonarr instances.
- **Configuration (`config.json`)**:
  - Default settings file, editable manually or via UI.
  - Overridable by environment variables for flexibility.
- **Docker Setup (`Dockerfile`)**:
  - Lightweight Python 3.9-slim base image.
  - Installs dependencies and exposes port 5000.
- **Dependencies (`requirements.txt`)**:
  - Lists Python packages: Flask, requests, Flask-SocketIO, schedule, python-environ.

## Settings
Settings are fully configurable through the web UI, `config.json`, or environment variables:
- **`zurg_host`**:
  - Description: URL of the Zurg WebDAV server.
  - Example: `http://localhost:9999`.
- **`zurg_mount`**:
  - Description: Filesystem path to the Zurg mount.
  - Example: `/storage/realdebrid-zurg/__all__`.
- **`symlink_dirs`**:
  - Description: List of directories containing symlinks to scan.
  - Example: `["/storage/symlinks/movies", "/storage/symlinks/series"]`.
- **`mode`**:
  - Description: Operation mode for symlink handling.
  - Options:
    - `repair_only`: Repairs broken symlinks without removing unrepairable ones.
    - `repair_and_remove`: Repairs where possible, removes unrepairable symlinks, and notifies Arr instances.
  - Default: `repair_and_remove`.
- **`scan_interval`**:
  - Description: Minutes between scheduled scans (0 to disable).
  - Example: `30` (every 30 minutes).
  - Default: `0`.
- **`log_level`**:
  - Description: Logging verbosity level.
  - Options: `debug`, `info`, `warning`, `error`.
  - Default: `info`.
- **`radarr_instances`**:
  - Description: List of Radarr instances for notifications.
  - Format: `[{"name": "Radarr", "host": "http://localhost:7878", "api_key": "your_key"}, ...]`.
- **`sonarr_instances`**:
  - Description: List of Sonarr instances for notifications.
  - Format: `[{"name": "Sonarr", "host": "http://localhost:8989", "api_key": "your_key"}, ...]`.

## How to Use
1. **Launch the App**: Start via Docker (see installation below) and visit `http://localhost:5000`.
2. **Check Status**: The "Status" card shows Zurg’s availability (green for "Up," red for "Down"), updated live.
3. **Configure Settings**:
   - Navigate to the "Configuration" card.
   - Enter Zurg details (host, mount), symlink directories (comma-separated), mode, scan interval, and log level.
   - Add Radarr/Sonarr instances by clicking "Add Radarr" or "Add Sonarr," filling in name, host, and API key.
   - Click "Save Config" (restart required for scheduling changes).
4. **Run Scans**:
   - **Manual**: Click "Run Scan" in the "Actions" card to scan immediately.
   - **Scheduled**: Set `scan_interval` (e.g., `60` for hourly), save, and restart; scans run automatically.
5. **Monitor Results**: The "Scan Results" card updates in real-time with:
   - **Repaired Symlinks**: Table of paths and new targets.
   - **Removed Symlinks**: Table of deleted paths.
   - **Valid Symlinks**: Count of intact links.
   - **Status**: Idle, Running, Complete, or Zurg Down.

### Example Usage
- **Manual Scan**: Set `zurg_host` to `http://zurg:9999`, `symlink_dirs` to `/storage/symlinks/movies`, click "Run Scan," and see broken links repaired or removed.
- **Scheduled Scan**: Set `scan_interval` to `1440` (daily), save, restart, and check results daily at `http://localhost:5000`.

## How to Install

### Prerequisites
- Docker (recommended) or Python 3.9+ (for local runs).
- Zurg running with WebDAV access.
- Radarr/Sonarr (optional, for notifications).
- Read/write access to symlink and Zurg mount directories.

### Docker Installation
1. **Clone the Repo**:
   ```bash
   git clone https://github.com/bsm-elf/symlink-cleaner.git
   cd symlink-cleaner```
2. **Configure**:
   - Edit `config.json` with your Zurg host, mount, and Arr API keys.
   - Or use env vars (see below).
3. **Build and Run**:

   ```bash
   docker build -t symlink-cleaner .
   docker run -v ./config.json:/app/config.json -v /storage:/storage -p 5000:5000 symlink-cleaner```

   **With env vars:**

   ```bash docker run -v ./config.json:/app/config.json -v /storage:/storage -p 5000:5000 \ -e ZURG_HOST=http://zurg:9999 -e SCAN_INTERVAL=60 -e LOG_LEVEL=debug symlink-cleaner```

4. **Verify**: Open `http://localhost:5000`.

## Environment Variables

| Variable         | Description                            | Example Value                  | Default (from `config.json`) |
|-------------------|----------------------------------------|--------------------------------|------------------------------|
| `ZURG_HOST`      | Zurg WebDAV URL                       | `http://zurg:9999`            | `http://localhost:9999`      |
| `ZURG_MOUNT`     | Zurg mount path                       | `/mnt/zurg/__all__`           | `/storage/realdebrid-zurg/__all__` |
| `SYMLINK_DIRS`   | Comma-separated symlink directories   | `/path1,/path2`               | See `config.json`            |
| `MODE`           | Operation mode                        | `repair_and_remove`           | `repair_and_remove`          |
| `SCAN_INTERVAL`  | Minutes between scans (0 to disable)  | `30`                          | `0`                          |
| `LOG_LEVEL`      | Logging verbosity                     | `debug`                       | `info`                       |
| `SECRET_KEY`     | Flask secret key (security)           | `random_string_123`           | `your-secret-key`            |

**Note**: `radarr_instances` and `sonarr_instances` are configured via UI or `config.json` only due to their list structure.

## Troubleshooting
- **Zurg Down**: Ensure Zurg is running and accessible at the specified `zurg_host`.
- **No Scans**: Check `scan_interval` > 0 and restart after saving.
- **Permission Errors**: Verify Docker container has read/write access to mounted directories.
- **Slow UI Updates**: Remove `time.sleep(0.1)` in `symlink_cleaner.py` (demo artifact).

## Notes
- **Security**: Set `SECRET_KEY` via env var in production.
- **Restart**: Scheduling changes require a restart.
- **Contributions**: Fork and PR on GitHub!





