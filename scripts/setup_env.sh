#!/bin/bash
# Helper to prepare a control host (Ubuntu/Debian/macOS) with Ansible & essentials.
# macOS notes: prefer Homebrew. Debian/Ubuntu will use apt.
set -euo pipefail

OS="$(uname -s)"

if [ "$OS" = "Darwin" ]; then
  echo "Detected macOS. Using Homebrew / pip fallback..."
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Install Homebrew or use 'pip3 install --user ansible'."
    echo "Visit https://brew.sh to install Homebrew."
    exit 1
  fi
  echo "Installing ansible via brew..."
  brew update
  brew install ansible
else
  echo "Assuming Linux (Debian/Ubuntu). Installing apt packages..."
  sudo apt update
  sudo apt install -y software-properties-common
  sudo add-apt-repository --yes --update ppa:ansible/ansible
  sudo apt install -y ansible git python3-pip
  pip3 install --user docker-compose
fi

echo ""
echo "Done. Place your inventory at ansible/inventory.ini and run:"
echo "  ansible-playbook -i ansible/inventory.ini ansible/site.yml"
