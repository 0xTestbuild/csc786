# Retrying creation of the starter repository for the Deception-Enhanced Red Team Training Lab.
import os, textwrap, json, stat, shutil

base_dir = "/mnt/data/deception_cyberlab"
if os.path.exists(base_dir):
    shutil.rmtree(base_dir)
os.makedirs(base_dir, exist_ok=True)

# README.md
readme = textwrap.dedent("""\
# Deception-Enhanced Red Team Training Lab (Starter Repo)

**Author:** Darold Kelly Jr.
**Purpose:** Practical-pathway starter code for Assignment 4 (CSC786). This repository provides orchestration, deception controller skeleton, and evaluation scripts for a small, isolated cyber range (2 Windows hosts + 1 Linux bastion in the design).

**Important safety note:** This code is intended for **isolated, offline lab environments only**. Do NOT deploy services (honeypots, emulators, or attack tooling) on public networks. Obtain necessary approvals before running exercises with human participants.

## Contents
- `ansible/` - Ansible inventory and playbook to provision lab hosts (installs Docker & Docker Compose).
- `docker/` - `docker-compose.yml` to run honeypot (Cowrie), ELK logging stack (Elasticsearch + Kibana + Logstash) for collection, and a placeholder for Caldera (adversary emulation) if desired.
- `deception_controller/` - Python skeleton that monitors logs and updates deception artifacts (honeytokens).
- `scoring/` - Scripts to compute detection metrics (detection accuracy, MTTD) from collected logs.
- `scripts/setup_env.sh` - Helper shell script to prepare a single Ubuntu host for Ansible control and Docker usage.

## How to use (high-level)
1. Ensure a fully isolated virtual network (no route to the public internet).
2. Provision VMs (Ubuntu 22.04 recommended) and populate `ansible/inventory.ini` with their IPs.
3. Run the Ansible playbook: `ansible-playbook -i ansible/inventory.ini ansible/site.yml`
4. SSH into the orchestrator / control host and `cd docker` then `docker compose up -d` to start services.
5. Start the deception controller: `python3 deception_controller/deception_controller.py` (requires Python 3.9+)
6. Use Caldera or your red team tooling within the isolated lab to run simulated attacks. **Do not** share attack payloads or enable external access.
7. Use `scoring/scoring.py` to parse logs and compute metrics after sessions.

## Ethical & Safety
- This lab must remain isolated.
- Participant consent, anonymization, and IRB approvals (if applicable) must be obtained.
- The deception controller intentionally contains placeholders for adaptive logic so you can implement policies safely.

""")

with open(os.path.join(base_dir, "README.md"), "w") as f:
    f.write(readme)

# ansible files
os.makedirs(os.path.join(base_dir, "ansible"), exist_ok=True)
inventory = textwrap.dedent("""\
[lab_hosts]
host1 ansible_host=10.0.50.11 ansible_user=ubuntu
host2 ansible_host=10.0.50.12 ansible_user=ubuntu
bastion ansible_host=10.0.50.10 ansible_user=ubuntu

[all:vars]
ansible_python_interpreter=/usr/bin/python3
""")
with open(os.path.join(base_dir, "ansible", "inventory.ini"), "w") as f:
    f.write(inventory)

site_yml = textwrap.dedent("""\
---
- name: Prepare lab hosts for deception cyber range
  hosts: lab_hosts
  become: true
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Install required packages
      apt:
        name:
          - apt-transport-https
          - ca-certificates
          - curl
          - gnupg
          - lsb-release
          - python3-pip
        state: present

    - name: Install Docker GPG key
      apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        state: present

    - name: Add Docker repository
      apt_repository:
        repo: deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_lsb.codename }} stable
        state: present

    - name: Install Docker and Docker Compose plugin
      apt:
        name:
          - docker-ce
          - docker-ce-cli
          - containerd.io
        state: present
      register: docker_install
      ignore_errors: yes

    - name: Ensure user is in docker group
      user:
        name: "{{ ansible_user }}"
        groups: docker
        append: yes

    - name: Create directories for deception artifacts and logs
      file:
        path: /opt/deception_lab/{{ item }}
        state: directory
        owner: "{{ ansible_user }}"
        mode: '0755'
      loop:
        - honeytokens
        - logs
        - cowrie

    - name: Install docker-compose (pip fallback)
      pip:
        name: docker-compose
        executable: pip3
      when: docker_install is failed | default(False)
""")
with open(os.path.join(base_dir, "ansible", "site.yml"), "w") as f:
    f.write(site_yml)

# docker compose
os.makedirs(os.path.join(base_dir, "docker"), exist_ok=True)
docker_compose = textwrap.dedent("""\
version: '3.8'
services:

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.1
    container_name: es
    environment:
      - discovery.type=single-node
      - \"ES_JAVA_OPTS=-Xms512m -Xmx512m\"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - esdata:/usr/share/elasticsearch/data
    networks:
      - deception_net

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.1
    container_name: kibana
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    ports:
      - \"5601:5601\"
    networks:
      - deception_net

  cowrie:
    image: cowrie/cowrie:latest
    container_name: cowrie
    restart: unless-stopped
    volumes:
      - ./cowrie/data:/cowrie/data
    networks:
      - deception_net

  caldera:
    image: mitre/caldera:4.3.0
    container_name: caldera
    environment:
      - ADMIN_USER=admin
      - ADMIN_PASSWORD=admin
    ports:
      - \"8888:8888\"
    networks:
      - deception_net

volumes:
  esdata:

networks:
  deception_net:
    driver: bridge
""")
with open(os.path.join(base_dir, "docker", "docker-compose.yml"), "w") as f:
    f.write(docker_compose)

# scripts
os.makedirs(os.path.join(base_dir, "scripts"), exist_ok=True)
setup_sh = textwrap.dedent("""\
#!/bin/bash
# Simple helper to install ansible & basic tools on control host (Ubuntu/Debian).
set -euo pipefail
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install -y ansible git python3-pip
pip3 install --user docker-compose
echo "Environment ready. Place inventory in ansible/inventory.ini and run: ansible-playbook -i ansible/inventory.ini ansible/site.yml"
""")
with open(os.path.join(base_dir, "scripts", "setup_env.sh"), "w") as f:
    f.write(setup_sh)
os.chmod(os.path.join(base_dir, "scripts", "setup_env.sh"), 0o755)

# deception_controller
os.makedirs(os.path.join(base_dir, "deception_controller"), exist_ok=True)
deception_py = textwrap.dedent("""\
#!/usr/bin/env python3
\"\"\"Adaptive Deception Controller (skeleton)
- Watches Cowrie log directory (or Elasticsearch) for attacker events
- Deploys or rotates honeytokens on lab hosts via SSH or Ansible
- Publishes a short audit log for scoring pipelines

IMPORTANT: This is a safe skeleton for educational use. Implement adaptive policies cautiously,
and only run in isolated lab environments.
\"\"\"

import os
import time
import json
import logging
import subprocess
from datetime import datetime

# Configuration - edit for your lab
COWRIE_LOG_DIR = '/opt/deception_lab/logs/cowrie'  # or path mounted from cowrie container
HONEYTOKEN_DIR = '/opt/deception_lab/honeytokens'
AUDIT_LOG = '/opt/deception_lab/logs/deception_controller_audit.log'
CHECK_INTERVAL = 5  # seconds

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def scan_cowrie_logs(log_dir):
    \"\"\"Scan for new Cowrie JSON log files and yield parsed events.\"\"\"
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

def place_honeytoken(host, token_content, token_name):
    \"\"\"Place a honeytoken file on a host.
    This skeleton uses Ansible ad-hoc command to copy content to /opt/deception_lab/honeytokens on the target host.
    Adjust for your environment (SSH keys, user, paths).\"\"\"
    target = host
    local_tmp = f'/tmp/{token_name}'
    with open(local_tmp, 'w') as fh:
        fh.write(token_content)
    cmd = ['ansible', target, '-m', 'copy', '-a', f'src={local_tmp} dest=/opt/deception_lab/honeytokens/{token_name} mode=0644']
    logging.info('Placing honeytoken %s on %s', token_name, host)
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logging.exception('Ansible copy failed: %s', e)

def record_audit(entry):
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    with open(AUDIT_LOG, 'a') as fh:
        fh.write(json.dumps(entry) + '\\n')

def main_loop():
    processed = set()
    logging.info('Starting Deception Controller (skeleton). Check interval: %s sec', CHECK_INTERVAL)
    while True:
        for event in scan_cowrie_logs(COWRIE_LOG_DIR):
            # Use 'session' or 'src_ip' or 'username' fields to identify interactions
            event_id = event.get('session', '') + '|' + event.get('src_ip', '') + '|' + str(event.get('timestamp', ''))
            if event_id in processed:
                continue
            processed.add(event_id)
            # Simple adaptive policy:
            # If attacker attempted to access a decoy filename pattern, rotate a honeytoken to that host
            src_ip = event.get('src_ip', 'unknown')
            username = event.get('username', '')
            cmd = event.get('message', '') or event.get('eventid', '')
            logging.info('Observed event from %s: %s', src_ip, cmd)
            # Place a honeytoken with contextual content (do NOT put real credentials)
            token_name = f'honey_{int(time.time())}.txt'
            token_content = f'INSTR: Investigate file {token_name} - created by deception controller at {datetime.utcnow().isoformat()}'
            # For lab safety, target host resolution should map src_ip to lab host inventory names (host1/host2)
            # Here we choose a conservative policy: place token on both lab hosts via Ansible group 'lab_hosts'
            place_honeytoken('lab_hosts', token_content, token_name)
            audit = {
                'timestamp': datetime.utcnow().isoformat(),
                'action': 'place_honeytoken',
                'token': token_name,
                'src_ip': src_ip,
                'username': username
            }
            record_audit(audit)
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main_loop()
""")
with open(os.path.join(base_dir, "deception_controller", "deception_controller.py"), "w") as f:
    f.write(deception_py)
os.chmod(os.path.join(base_dir, "deception_controller", "deception_controller.py"), 0o755)

# scoring
os.makedirs(os.path.join(base_dir, "scoring"), exist_ok=True)
scoring_py = textwrap.dedent("""\
#!/usr/bin/env python3
\"\"\"Simple scoring pipeline
- Reads deception controller audit log and cowrie logs (or Elasticsearch export)
- Computes:
  - detection accuracy (placeholder calculation)
  - mean time to detect (MTTD) as time between first attacker event and first detection alert
This script is intentionally conservative: it expects structured logs and does not parse attack payloads.
\"\"\"

import os
import json
import statistics
from datetime import datetime

AUDIT_LOG = '/opt/deception_lab/logs/deception_controller_audit.log'  # produced by controller
COWRIE_LOG_DIR = '/opt/deception_lab/logs/cowrie'


def parse_audit(audit_path):
    events = []
    if not os.path.exists(audit_path):
        return events
    with open(audit_path, 'r') as fh:
        for line in fh:
            try:
                events.append(json.loads(line.strip()))
            except Exception:
                continue
    return events

def parse_cowrie(cowrie_dir):
    events = []
    if not os.path.isdir(cowrie_dir):
        return events
    for fname in sorted(os.listdir(cowrie_dir)):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(cowrie_dir, fname)
        with open(path, 'r') as fh:
            for line in fh:
                try:
                    e = json.loads(line.strip())
                    events.append(e)
                except Exception:
                    continue
    return events

def compute_mttd(cowrie_events, detection_events):
    # Very conservative: match by src_ip; compute time diff between first attacker event and first detection audit
    times = []
    if not cowrie_events or not detection_events:
        return None
    first_by_ip = {}
    for e in cowrie_events:
        ip = e.get('src_ip')
        ts = e.get('timestamp')
        if ip and ts:
            first_by_ip.setdefault(ip, ts)
    for d in detection_events:
        ip = d.get('src_ip')
        ts = d.get('timestamp')
        if ip and ts and ip in first_by_ip:
            try:
                t1 = datetime.fromisoformat(first_by_ip[ip])
                t2 = datetime.fromisoformat(ts)
                delta = (t2 - t1).total_seconds()
                times.append(delta)
            except Exception:
                continue
    if not times:
        return None
    return statistics.mean(times)

def main():
    audit = parse_audit(AUDIT_LOG)
    cowrie = parse_cowrie(COWRIE_LOG_DIR)
    mttd = compute_mttd(cowrie, audit)
    print('Audit events:', len(audit))
    print('Cowrie events:', len(cowrie))
    print('Estimated MTTD (seconds):', mttd)

if __name__ == '__main__':
    main()
""")
with open(os.path.join(base_dir, "scoring", "scoring.py"), "w") as f:
    f.write(scoring_py)
os.chmod(os.path.join(base_dir, "scoring", "scoring.py"), 0o755)

# .gitignore
with open(os.path.join(base_dir, ".gitignore"), "w") as f:
    f.write("*.pyc\n__pycache__/\n.vscode/\n.env\n")

# create zip
zip_path = "/mnt/data/deception_cyberlab.zip"
if os.path.exists(zip_path):
    os.remove(zip_path)
shutil.make_archive("/mnt/data/deception_cyberlab", 'zip', base_dir)

print("Created starter repo at:", base_dir)
print("Zipped repo for download at:", zip_path)