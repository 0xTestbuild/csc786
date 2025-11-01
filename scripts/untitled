#!/usr/bin/env python3
"""
Simple scoring pipeline
- Reads deception controller audit log and cowrie logs (or Elasticsearch export)
- Computes:
  - Estimated mean time to detect (MTTD)
  - Counts of honeytoken placements and interactions

Assumptions:
- Cowrie JSON logs have 'src_ip' and 'timestamp' fields (ISO format)
- Audit log is produced by deception_controller and contains 'timestamp' and 'src_ip'
"""

import os
import json
import statistics
from datetime import datetime

BASE_DIR = os.path.expanduser(os.environ.get("DECEPTION_BASE", "~/deception_lab"))
AUDIT_LOG = os.path.join(BASE_DIR, "logs", "deception_controller_audit.log")
COWRIE_LOG_DIR = os.path.join(BASE_DIR, "logs", "cowrie")

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
    # Match by src_ip; compute time diff between the first attacker event and first detection action
    times = []
    if not cowrie_events or not detection_events:
        return None
    first_by_ip = {}
    for e in cowrie_events:
        ip = e.get('src_ip')
        ts = e.get('timestamp')
        if ip and ts:
            # Normalize timestamp if numeric
            try:
                # If timestamp is numeric (epoch), convert
                if isinstance(ts, (int, float)):
                    t_iso = datetime.utcfromtimestamp(ts).isoformat() + "Z"
                else:
                    t_iso = ts
                first_by_ip.setdefault(ip, t_iso)
            except Exception:
                continue
    for d in detection_events:
        ip = d.get('src_ip')
        ts = d.get('timestamp')
        if ip and ts and ip in first_by_ip:
            try:
                t1 = datetime.fromisoformat(first_by_ip[ip].replace("Z",""))
                t2 = datetime.fromisoformat(ts.replace("Z",""))
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
    print("Audit events:", len(audit))
    print("Cowrie events:", len(cowrie))
    print("Estimated MTTD (seconds):", mttd)

if __name__ == "__main__":
    main()
