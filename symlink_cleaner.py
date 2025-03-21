import os
import json
import logging
import requests
from flask import Flask, jsonify, request, render_template
import argparse

app = Flask(__name__, template_folder='templates', static_folder='static')
logger = logging.getLogger(__name__)

def check_zurg_status(zurg_host):
    """Check if Zurg's WebDAV server is up."""
    try:
        response = requests.head(f"{zurg_host}/dav/__all__/", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        logger.error("Zurg is not responding")
        return False

def repair_symlink(symlink_path, zurg_mount):
    """Repair a symlink by looking for a similar file in the original target directory."""
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
    """Notify Radarr/Sonarr instances when a symlink is removed."""
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

def clean_symlinks(config):
    """Scan and manage symlinks, only if Zurg is up."""
    if not check_zurg_status(config["zurg_host"]):
        logger.error("Zurg is down, aborting symlink scan")
        return {"status": "zurg_down"}
    
    mode = config.get("mode", "repair_and_remove")
    results = {"repaired": [], "removed": [], "valid": 0}
    for dir_path in config["symlink_dirs"]:
        for root, _, files in os.walk(dir_path):
            for file in files:
                symlink_path = os.path.join(root, file)
                if os.path.islink(symlink_path):
                    repaired, new_target = repair_symlink(symlink_path, config["zurg_mount"])
                    if repaired and new_target != os.readlink(symlink_path):
                        results["repaired"].append({"path": symlink_path, "new_target": new_target})
                    elif not repaired and mode == "repair_and_remove":
                        os.remove(symlink_path)
                        notify_arr_instances(config, symlink_path)
                        results["removed"].append(symlink_path)
                    else:
                        results["valid"] += 1
    logger.info(f"Scan complete: {len(results['repaired'])} repaired, {len(results['removed'])} removed, {results['valid']} valid")
    return results

@app.route('/')
def index():
    with open(app.config['config_file']) as f:
        config = json.load(f)
    zurg_up = check_zurg_status(config["zurg_host"])
    return render_template('index.html', zurg_status="Up" if zurg_up else "Down")

@app.route('/config', methods=['GET', 'POST'])
def config_endpoint():
    config_file = app.config['config_file']
    if request.method == 'POST':
        with open(config_file, 'w') as f:
            json.dump(request.json, f, indent=2)
        return jsonify({"status": "saved"})
    with open(config_file) as f:
        return jsonify(json.load(f))

@app.route('/scan', methods=['POST'])
def scan():
    with open(app.config['config_file']) as f:
        config = json.load(f)
    logging.basicConfig(level=config.get("log_level", "INFO").upper())
    results = clean_symlinks(config)
    return jsonify(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Symlink Cleaner for Zurg")
    parser.add_argument('--config', default='config.json', help="Path to config file")
    args = parser.parse_args()
    app.config['config_file'] = args.config
    app.run(host='0.0.0.0', port=5000)