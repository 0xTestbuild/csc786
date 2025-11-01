#!/usr/bin/env python3
"""
Adaptive Deception Controller (skeleton)
- Watches Cowrie log directory (or Elasticsearch) for attacker events
- Deploys or rotates honeytokens on lab hosts via Ansible
- Publishes a short audit log for scoring pipelines

Configuration:
- Optional environment variable DECEPTION_BASE sets base path (default: ~/deception_lab)
- The controller will write audit logs under BASE/logs and place tokens under BASE/honeytokens

IMPORTANT: Run only in an isolated lab environment. Do not place real credentials in honeytokens.
"""

import os
import time
import json
import logging
import subprocess
from datetime import datetime

# Configurable base directory (use env var DECEPTION_BASE to override)
BASE_DIR = os.path.expanduser(os.environ.get("DECEPTION_BASE", "~/deception_lab"))
COWRIE_LOG_DIR = os.path.join(BASE_DIR, "logs", "cowrie")
HONEYTOKEN_DIR = os.path.join(BASE_DIR, "honeytokens")
AUDIT_LOG = os.path.join(BASE_DIR, "logs", "deception_controller_audit.log")
CHECK_INTERVAL = int(os.environ.get("DECEPTION_CHECK_INTERVAL", "5"))  # seconds

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def ensure_directories():
    os.makedirs(COWRIE_LOG_DIR, exist_ok=True)
    os.makedirs(HONEYTOKEN_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)

def scan_cowrie_logs(log_dir):
    """Scan for new Cowrie JSON log files and yield parsed events."""
    if not os.path.isdir(log_dir):
        logging.warning('Cowrie log dir does not exist: %s', log_dir)
        return
    for fname in sorted(os.listdir(log_dir)):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(log_dir, fname)
        try:
            with open(path, 'r') as fh:
                for line in fh:
                    try:
                        event = json.loads(line.strip())
                        yield event
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logging.exception('Failed to read cowrie log %s: %s', path, e)

def place_honeytoken(target_group, token_content, token_name):
    """
    Place a honeytoken file on target group via Ansible ad-hoc copy.
    - target_group: Ansible inventory host or group (e.g., 'host1', 'lab_hosts')
    - token_content: string to write
    - token_name: filename such as honey_12345.txt
    """
    local_tmp = os.path.join("/tmp", token_name)
    with open(local_tmp, 'w') as fh:
        fh.write(token_content)

    cmd = ['ansible', target_group, '-m', 'copy', '-a',
           f"src={local_tmp} dest=/opt/deception_lab/honeytokens/{token_name} mode=0644"]
    logging.info('Placing honeytoken %s on %s', token_name, target_group)
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logging.exception('Ansible copy failed: %s', e)

def record_audit(entry):
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    with open(AUDIT_LOG, 'a') as fh:
        fh.write(json.dumps(entry) + '\n')

def map_srcip_to_target(src_ip):
    """
    Conservative default mapping:
    - If lab hosts are NATed or static IPs, set mapping logic here.
    - For now, return 'lab_hosts' (group) to place token on all lab hosts.
    Customize for your inventory.
    """
    return "lab_hosts"

def main_loop():
    ensure_directories()
    processed = set()
    logging.info('Starting Deception Controller. Check interval: %s sec', CHECK_INTERVAL)
    while True:
        for event in scan_cowrie_logs(COWRIE_LOG_DIR):
            # Use 'session' or 'src_ip' or 'username' fields to identify interactions
            src_ip = event.get('src_ip') or event.get('src_ip', 'unknown')
            session = event.get('session') or ''
            timestamp = event.get('timestamp') or ''
            event_id = f"{session}|{src_ip}|{timestamp}"
            if event_id in processed:
                continue
            processed.add(event_id)

            username = event.get('username', '')
            message = event.get('message', '') or event.get('eventid', '')
            logging.info('Observed event from %s: %s', src_ip, message)

            # Simple adaptive policy:
            # Rotate a honeytoken whenever an interactive session or login attempt is observed.
            token_name = f"honey_{int(time.time())}.txt"
            token_content = (
                f"INSTR: Investigate file {token_name}\n"
                f"Created by deception controller at {datetime.utcnow().isoformat()}Z\n"
                "NOTE: This file is a decoy. Do not use as a credential.\n"
            )

            target = map_srcip_to_target(src_ip)
            place_honeytoken(target, token_content, token_name)

            audit = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "action": "place_honeytoken",
                "token": token_name,
                "src_ip": src_ip,
                "username": username,
                "reason": message
            }
            record_audit(audit)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
