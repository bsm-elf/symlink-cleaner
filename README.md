# Symlink Cleaner

Symlink Cleaner is a tool for managing symbolic links in a Zurg mount. It scans symlink directories, identifies files that are no longer linked, and either removes them or repairs broken symlinks. It includes a **dashboard-style web UI** for monitoring and managing the cleanup process.

## Features
- **Detects unlinked files** in Zurg and removes them.
- **Repairs broken symlinks** by finding the correct file.
- **Deletes irreparable symlinks** if no match is found.
- **Dashboard UI** with filters, charts, and controls.
- **Dry-run mode** to preview changes before execution.
- **Dockerized setup** for easy deployment.

## Default Configuration
- **Zurg Mount Directory:** `/storage/realdebrid-zurg/__all__/`
- **Symlink Directories:**
  - `/storage/symlinks/anime_movies/`
  - `/storage/symlinks/anime_shows/`
  - `/storage/symlinks/movies/`
  - `/storage/symlinks/movies-4k/`
  - `/storage/symlinks/series/`
  - `/storage/symlinks/series-4k/`

## Installation
### Prerequisites
- **Docker & Docker Compose** installed on your machine.
- **Git** (if cloning from GitHub).

### Setup
#### 1. Clone the Repository
```sh
git clone https://github.com/YOUR_USERNAME/symlink-cleaner.git
cd symlink-cleaner
```

#### 2. Configure the App
Edit `config.json` to customize the settings:
```json
{
  "symlink_dirs": [
    "/storage/symlinks/anime_movies/",
    "/storage/symlinks/anime_shows/",
    "/storage/symlinks/movies/",
    "/storage/symlinks/movies-4k/",
    "/storage/symlinks/series/",
    "/storage/symlinks/series-4k/"
  ],
  "zurg_mount": "/storage/realdebrid-zurg/__all__/",
  "dry_run": true
}
```

#### 3. Build and Run with Docker
```sh
docker-compose up --build
```
This will start both the **backend (Go)** and **frontend (React)** services.

## Usage
### Access the Web UI
Once running, open your browser and go to:
```
http://localhost:3000
```

### Available Features in UI
- **Toggle Dry Run Mode**: Preview deletions before execution.
- **Run Cleanup & Repair**: Execute symlink cleanup operations.
- **View Charts**: See symlinked vs. unlinked file stats.
- **Check Broken Symlinks**: See which symlinks were repaired or deleted.

## Logs & Debugging
- Backend logs: `logs/backend.log`
- Frontend logs: `logs/frontend.log`
- View logs in real-time:
  ```sh
  docker logs -f symlink-cleaner-backend
  ```

## Environment Variables
You can override default settings using the following environment variables:
- **`SYMLINK_DIRS`**: Comma-separated list of directories to scan for symlinks.
  ```sh
  SYMLINK_DIRS="/custom/path1,/custom/path2"
  ```
- **`ZURG_MOUNT`**: Path to the Zurg mount directory.
  ```sh
  ZURG_MOUNT="/custom/zurg/path"
  ```
- **`DRY_RUN`**: Set to `true` to preview deletions, `false` to execute.
  ```sh
  DRY_RUN=false
  ```

## Contributing
Feel free to **fork the repository** and submit **pull requests**!

## License
This project is licensed under the MIT License.

---

Need help? Open an issue on **GitHub** or ask in the discussions tab! 🚀
