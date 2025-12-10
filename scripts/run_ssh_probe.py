#!/usr/bin/env python3
"""
run_ssh_probe.py

Simple SSH probe for generating attacker-like events against Cowrie.
- Attempts SSH logins from a small credential list.
- Records each attempt to a CSV for later scoring and plotting.
- Safe for isolated labs. Do not use on production machines.

Usage example:
  pip3 install paramiko
  python3 tools/run_ssh_probe.py --host 127.0.0.1 --port 2222 --attempts 50 --out probe_results.csv

Outputs:
- CSV with columns: timestamp_iso, target_host, target_port, username, password, result, latency_ms

"""
import argparse
import csv
import time
from datetime import datetime
import socket

import paramiko

# Default credential list - synthetic only
DEFAULT_CREDS = [
    ("root", "toor"),
    ("admin", "admin"),
    ("guest", "guest"),
    ("ubuntu", "ubuntu"),
    ("test", "test123"),
    ("oracle", "oracle"),
    ("svcacct", "P@ssw0rd!"),
]

def try_ssh(host, port, username, password, timeout=8.0):
    """
    Try an SSH connection using Paramiko.
    Returns tuple: (result_str, latency_ms)
    result_str: "success", "auth_failed", "conn_refused", "timeout", "other_error"
    """
    start = time.time()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, port=port, username=username, password=password,
                       look_for_keys=False, allow_agent=False, banner_timeout=5.0,
                       auth_timeout=5.0, timeout=timeout)
        # if connection succeeds, try a harmless command
        try:
            stdin, stdout, stderr = client.exec_command("echo probe-ok", timeout=5.0)
            _ = stdout.read()
        except Exception:
            pass
        client.close()
        latency = int((time.time() - start) * 1000)
        return "success", latency
    except paramiko.ssh_exception.AuthenticationException:
        latency = int((time.time() - start) * 1000)
        return "auth_failed", latency
    except (paramiko.ssh_exception.SSHException, socket.timeout) as e:
        latency = int((time.time() - start) * 1000)
        # Distinguish connection refused vs timeout
        err = str(e).lower()
        if "timed out" in err or isinstance(e, socket.timeout):
            return "timeout", latency
        return "conn_error", latency
    except ConnectionRefusedError:
        latency = int((time.time() - start) * 1000)
        return "conn_refused", latency
    except Exception:
        latency = int((time.time() - start) * 1000)
        return "other_error", latency

def main():
    parser = argparse.ArgumentParser(description="SSH probe generator for Cowrie honeypot")
    parser.add_argument("--host", default="127.0.0.1", help="Target host (Cowrie). Default 127.0.0.1")
    parser.add_argument("--port", type=int, default=2222, help="Target SSH port. Default 2222 for Cowrie")
    parser.add_argument("--attempts", type=int, default=30, help="Total login attempts to perform")
    parser.add_argument("--out", default="probe_results.csv", help="CSV output file")
    parser.add_argument("--creds-file", default=None, help="Optional file with username:password per line")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between attempts (default 1.0)")
    args = parser.parse_args()

    creds = list(DEFAULT_CREDS)
    if args.creds_file:
        try:
            with open(args.creds_file, "r") as fh:
                creds = []
                for line in fh:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    u, p = line.split(":", 1)
                    creds.append((u.strip(), p.strip()))
        except FileNotFoundError:
            print("Creds file not found, using defaults")

    # Rotate through credentials
    total = args.attempts
    out_path = args.out
    fieldnames = ["timestamp_iso", "target_host", "target_port", "username", "password", "result", "latency_ms"]

    with open(out_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(total):
            u, p = creds[i % len(creds)]
            ts = datetime.utcnow().isoformat() + "Z"
            result, latency = try_ssh(args.host, args.port, u, p)
            row = {
                "timestamp_iso": ts,
                "target_host": args.host,
                "target_port": args.port,
                "username": u,
                "password": p,
                "result": result,
                "latency_ms": latency,
            }
            writer.writerow(row)
            print(f"[{i+1}/{total}] {u}:{p} -> {result} ({latency} ms)")
            time.sleep(args.delay)

    print("Done. Results written to", out_path)

if __name__ == "__main__":
    main()
