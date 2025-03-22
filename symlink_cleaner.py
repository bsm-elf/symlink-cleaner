import os
import json
import logging
import requests
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import argparse
import threading
import time
import schedule
from environs import Env

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')  # Replace with a secure key
socketio = SocketIO(app, cors_allowed_origins="*")
logger = logging.getLogger(__name__)

# Global state for scan results and config
scan_results = {"repaired": [], "removed": [], "valid": 0, "cleaned": [], "status": "idle"}
config_global = {}

# Load environment variables
env = Env()
env.read_env()

def load_config(config_file):
    """Load config from file and override with env vars."""
    with open(config_file) as f:
        config = json.load(f)
    config['zurg_host'] = env.str('ZURG_HOST', config['zurg_host'])
    config['zurg_mount'] = env.str('ZURG_MOUNT', config['zurg_mount'])
    config['symlink_dirs'] = env.list('SYMLINK_DIRS', config['symlink_dirs'], subcast=str, delimiter=',')
    config['mode'] = env.str('MODE', config['mode'])
    config['log_level'] = env.str('LOG_LEVEL', config['log_level'])
    config['scan_interval'] = env.int('SCAN_INTERVAL', config.get('scan_interval', 0))  # 0 = no schedule
    # Validate mode
    valid_modes = ["repair", "repair_and_remove", "repair_and_remove_unused"]
    if config['mode'] not in valid_modes:
        raise ValueError(f"Invalid mode: {config['mode']}. Must be one of {valid_modes}")
    return config

def check_zurg_status(zurg_host):
    """Check if Zurg's WebDAV server is up."""
    try:
        response = requests.head(f"{zurg_host}/dav/__all__/", timeout=5)
        up = response.status_code == 200
        socketio.emit('zurg_status', {'status': 'Up' if up else 'Down'})
        return up
    except requests.RequestException:
        logger.error("Zurg is not responding")
        socketio.emit('zurg_status', {'status': 'Down'})
        return False

def repair_symlink(symlink_path, zurg_mount):
    target = os.readlink(symlink_path)
    if not os.path.exists(target):
        target_dir = os.path.dirname(target)
        if os.path.exists(target_dir):
            symlink_ext = os.path.splitext(symlink_path)[1]
            for file in os.listdir(target_dir):
                if os.path.splitext(file)[1] == symlink_ext:
                    new_target = os.path.join(target_dir, file)
                    os.remove(symlink_path)
                    os.symlink(new_target, symlink_path)
                    logger.info(f"Repaired {symlink_path} -> {new_target}")
                    return True, new_target
        logger.warning(f"Could not repair {symlink_path} (original target: {target})")
        return False, None
    logger.debug(f"Valid symlink: {symlink_path}")
    return True, target

def notify_arr_instances(config, symlink_path):
    for radarr in config.get("radarr_instances", []):
        try:
            headers = {"X-Api-Key": radarr["api_key"]}
            requests.post(f"{radarr['host']}/api/v3/command",
                         json={"name": "RefreshMovie", "files": [symlink_path]},
                         headers=headers)
            logger.info(f"Notified {radarr['name']} about {symlink_path}")
        except requests.RequestException as e:
            logger.error(f"Failed to notify {radarr['name']}: {e}")
    for sonarr in config.get("sonarr_instances", []):
        try:
            headers = {"X-Api-Key": sonarr["api_key"]}
            requests.post(f"{sonarr['host']}/api/v3/command",
                         json={"name": "RefreshSeries", "files": [symlink_path]},
                         headers=headers)
            logger.info(f"Notified {sonarr['name']} about {symlink_path}")
        except requests.RequestException as e:
            logger.error(f"Failed to notify {sonarr['name']}: {e}")

def clean_spare_files(config):
    """Delete files in Zurg directory that aren't symlinked to."""
    zurg_mount = config["zurg_mount"]
    symlink_dirs = config["symlink_dirs"]
    # Collect all targets referenced by symlinks
    referenced_targets = set()
    for dir_path in symlink_dirs:
        for root, _, files in os.walk(dir_path):
            for file in files:
                symlink_path = os.path.join(root, file)
                if os.path.islink(symlink_path):
                    target = os.readlink(symlink_path)
                    referenced_targets.add(os.path.abspath(target))

    # Scan Zurg directory for files not referenced by any symlink
    cleaned_files = []
    for root, _, files in os.walk(zurg_mount):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.abspath(file_path) not in referenced_targets:
                try:
                    os.remove(file_path)
                    cleaned_files.append(file_path)
                    logger.info(f"Deleted spare file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete spare file {file_path}: {e}")
    
    return cleaned_files

def clean_symlinks(config):
    global scan_results
    scan_results = {"repaired": [], "removed": [], "valid": 0, "cleaned": [], "status": "running"}
    socketio.emit('scan_update', scan_results)
    
    if not check_zurg_status(config["zurg_host"]):
        logger.error("Zurg is down, aborting symlink scan")
        scan_results["status"] = "zurg_down"
        socketio.emit('scan_update', scan_results)
        return
    
    mode = config.get("mode", "repair")
    for dir_path in config["symlink_dirs"]:
        for root, _, files in os.walk(dir_path):
            for file in files:
                symlink_path = os.path.join(root, file)
                if os.path.islink(symlink_path):
                    target = os.readlink(symlink_path)
                    if os.path.exists(target):
                        # Symlink is valid
                        scan_results["valid"] += 1
                    else:
                        # Symlink is broken
                        repaired, new_target = repair_symlink(symlink_path, config["zurg_mount"])
                        if repaired and new_target != os.readlink(symlink_path):
                            # Symlink was repaired
                            scan_results["repaired"].append({"path": symlink_path, "new_target": new_target})
                        elif not repaired and mode in ["repair_and_remove", "repair_and_remove_unused"]:
                            # Remove unrepairable symlinks in repair_and_remove or repair_and_remove_unused modes
                            os.remove(symlink_path)
                            notify_arr_instances(config, symlink_path)
                            scan_results["removed"].append(symlink_path)
                            logger.info(f"Removed unrepairable symlink: {symlink_path}")
                        else:
                            # In repair mode, leave unrepairable symlinks alone
                            logger.info(f"Symlink {symlink_path} could not be repaired and was left as-is")
                    socketio.emit('scan_update', scan_results)
    
    # If mode is repair_and_remove_unused, delete spare files in Zurg directory
    if mode == "repair_and_remove_unused":
        scan_results["cleaned"] = clean_spare_files(config)
    
    scan_results["status"] = "complete"
    logger.info(f"Scan complete: {len(scan_results['repaired'])} repaired, {len(scan_results['removed'])} removed, {scan_results['valid']} valid, {len(scan_results['cleaned'])} cleaned")
    socketio.emit('scan_update', scan_results)

def run_scheduler(config_file):
    """Run scheduled scans in a background thread."""
    def job():
        config = load_config(config_file)
        clean_symlinks(config)
    
    while True:
        config = load_config(config_file)
        interval = config['scan_interval']
        schedule.clear()  # Clear previous schedule
        if interval > 0:
            schedule.every(interval).minutes.do(job)
        schedule.run_pending()
        time.sleep(60)  # Check config changes every minute

@app.route('/')
def index():
    global config_global
    config_global = load_config(app.config['config_file'])
    return render_template('index.html', initial_status="Up" if check_zurg_status(config_global["zurg_host"]) else "Down")

@app.route('/config', methods=['GET', 'POST'])
def config_endpoint():
    config_file = app.config['config_file']
    if request.method == 'POST':
        with open(config_file, 'w') as f:
            json.dump(request.json, f, indent=2)
        global config_global
        config_global = load_config(config_file)
        return {"status": "saved"}
    return config_global

@socketio.on('start_scan')
def handle_scan():
    logging.basicConfig(level=config_global.get("log_level", "INFO").upper())
    threading.Thread(target=clean_symlinks, args=(config_global,)).start()

@socketio.on('connect')
def handle_connect():
    check_zurg_status(config_global["zurg_host"])
    emit('scan_update', scan_results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Symlink Cleaner for Zurg")
    parser.add_argument('--config', default='config.json', help="Path to config file")
    args = parser.parse_args()
    app.config['config_file'] = args.config
    
    # Load initial config and start scheduler
    config_global = load_config(args.config)
    threading.Thread(target=run_scheduler, args=(args.config,), daemon=True).start()
    
    socketio.run(app, host='0.0.0.0', port=5000)