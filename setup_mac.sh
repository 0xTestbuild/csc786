#!/bin/bash
# MacOS setup script for deception lab

echo "=== MacOS Control Host Setup ==="

# Check if Ansible is installed
if ! command -v ansible &> /dev/null; then
    echo "Installing Ansible via Homebrew..."
    brew install ansible
fi

# Check if SSH keys exist
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "Generating SSH key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

echo "=== Copying SSH keys to VMs ==="
for ip in 192.168.53.3 192.168.53.4 192.168.53.5; do
    echo "Setting up SSH key for $ip..."
    ssh-copy-id osboxes@$ip 2>/dev/null || {
        echo "Manual setup needed for $ip:"
        echo "  ssh osboxes@$ip"
        echo "  Password: osboxes.org"
    }
done

echo "=== Testing Ansible Connection ==="
ansible -i ansible/inventory.ini all -m ping

echo "=== Setup Complete ==="
echo "Next: Run 'ansible-playbook -i ansible/inventory.ini ansible/site.yml'"
