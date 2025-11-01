# Deception-Enhanced Red Team Training Lab (Starter Repo)

**Author:** Darold Kelly Jr.  
**Purpose:** Practical-pathway starter code for Assignment 4 (CSC786). This repository provides orchestration, a deception controller skeleton, and evaluation scripts for a small, isolated cyber range (2 Windows hosts + 1 Linux bastion in the design).

**Important safety note:** This code is intended for **isolated, offline lab environments only**. Do NOT deploy services (honeypots, emulators, or attack tooling) on public networks. Obtain necessary approvals before running exercises with human participants.

## Contents
- `ansible/` - Ansible inventory and playbook to provision lab hosts (installs Docker & Docker Compose).
- `docker/` - `docker-compose.yml` to run honeypot (Cowrie), ELK logging stack (Elasticsearch + Kibana), and a Caldera placeholder.
- `deception_controller/` - Python skeleton that monitors logs and rotates honeytokens.
- `scoring/` - Scripts to compute basic detection metrics (detection accuracy, MTTD).
- `scripts/` - helper and setup scripts.
- `.gitignore`

## Quickstart (high-level)
1. Ensure a fully isolated virtual network with no route to the public internet.
2. Place host IPs in `ansible/inventory.ini`.
3. From a control host with Ansible: `ansible-playbook -i ansible/inventory.ini ansible/site.yml`
4. On one lab host or control VM, `cd docker` and run `docker compose up -d` to start the logging stack & honeypot.
5. Update `DECEPTION_BASE` environment variable if you want a custom install location (defaults to `~/deception_lab`).
6. Run the deception controller: `python3 deception_controller/deception_controller.py`
7. Run red-team exercises inside the isolated lab (e.g., Caldera or manual tests). **DO NOT** enable external access.
8. Use `scoring/scoring.py` to compute MTTD and other simple metrics.

## Safety & Ethics
- Keep lab networks isolated.
- Obtain participant consent and anonymize logs.
- Do not use real credentials or sensitive data in honeytokens.
- The repository intentionally omits offensive payloads and automated attack playbooks.

## Contact
If you want extensions (Caldera API scaffolding, ML-driven deception policies, or ingestion to ELK), tell me which and I will add safe scaffolding.
# csc786
