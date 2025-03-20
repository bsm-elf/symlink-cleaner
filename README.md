# Symlink Cleaner

Symlink Cleaner is a tool for managing symbolic links in a Zurg mount. It scans symlink directories, identifies files that are no longer linked, and either removes them or repairs broken symlinks. It includes a **dashboard-style web UI** for monitoring and managing the cleanup process.

## Features
- **Detects unlinked files** in Zurg and removes them.
- **Repairs broken symlinks** by finding the correct file.
- **Deletes irreparable symlinks** if no match is found.
- **Dashboard UI** with filters, charts, and controls.
- **Dry-run mode** to preview changes before execution.
- **Dockerized setup** for easy deployment.

## Installation
### Setup
#### 1. Clone the Repository
```sh
git clone https://github.com/YOUR_USERNAME/symlink-cleaner.git
cd symlink-cleaner
```
#### 2. Build and Run with Docker
```sh
docker-compose up --build
```
Once running, open your browser and go to `http://localhost:3000`.

## Logs & Debugging
- Backend logs: `logs/backend.log`
- Frontend logs: `logs/frontend.log`

## Environment Variables
- `SYMLINK_DIRS`: Comma-separated list of directories to scan.
- `ZURG_MOUNT`: Path to the Zurg mount directory.
- `DRY_RUN`: `true` to preview deletions, `false` to execute.
- `ENABLE_REMOVAL`: `true` to remove unlinked files, `false` to disable.
- `ENABLE_REPAIR`: `true` to repair broken symlinks, `false` to disable.

## License
This project is licensed under the MIT License.
