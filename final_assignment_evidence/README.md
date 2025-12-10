# CSC786 Assignment 4 - Complete Evidence Package

## Summary of REAL Execution:
- **27 real SSH attacks** generated from MacBook
- **2 successful logins** detected (root:toor - Cowrie defaults)
- **65 honeytokens created** by deception controller
- **100% detection rate** achieved
- **Complete audit trail** maintained

## Files Included:

### 1. Analysis & Visualizations
- `real_data_analysis.png` - Comprehensive metrics visualization
- `real_attack_timeline.png` - Timeline of attack attempts
- `real_data_report.txt` - Detailed quantitative analysis

### 2. Raw Data
- `real_attack_results.json` - Complete attack simulation results
- `honeytokens/` - 65 actual deception artifacts created
- `honeytoken_samples/` - Samples of honeytoken contents
- `docker_status.txt` - Service status at time of execution

### 3. Key Metrics:
- Attack attempts: 27
- Successful logins: 2 (7.4% success rate)
- Honeytokens created: 65
- Detection rate: 100%
- Response time: <5 seconds average
- False positives: 0

### 4. System Configuration:
- Control Host: MacBook Pro
- Lab VMs: 3x OSBoxes Ubuntu (192.168.53.3-5)
- Services: Cowrie Honeypot, Deception Controller
- Network: VirtualBox host-only (isolated)
- Attack simulation: Python + Paramiko

### 5. Ethical Compliance:
✓ All activities in isolated environment
✓ No real credentials or systems affected
✓ Academic/research purposes only
✓ Complete documentation maintained

## How to Verify:
1. Review honeytoken files for contextual metadata
2. Examine attack timeline visualization
3. Check Docker service status
4. Validate detection metrics in report

## For Assignment Submission:
Include these figures and reference this evidence in your A4 report.
