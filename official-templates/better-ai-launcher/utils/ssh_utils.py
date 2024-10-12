import os
import subprocess
import json

SSH_CONFIG_FILE = '/etc/ssh/sshd_config'
SSH_PASSWORD_FILE = '/workspace/.ssh_password'

def save_ssh_password(password):
    with open(SSH_PASSWORD_FILE, 'w') as f:
        json.dump({'password': password}, f)

def get_ssh_password():
    if os.path.exists(SSH_PASSWORD_FILE):
        with open(SSH_PASSWORD_FILE, 'r') as f:
            data = json.load(f)
            return data.get('password')
    return None

def check_ssh_config():
    try:
        with open('/etc/ssh/sshd_config', 'r') as f:
            config = f.read()
        
        root_login = 'PermitRootLogin yes' in config.split('\n')
        password_auth = 'PasswordAuthentication yes' in config.split('\n')
        
        print(f"Root login enabled: {root_login}")
        print(f"Password authentication enabled: {password_auth}")
        
        return root_login, password_auth
    except Exception as e:
        print(f"Error checking SSH config: {e}")
        return False, False

def setup_ssh():
    try:
        print("Setting up SSH configuration...")

        # Check for SSH host keys
        print("Checking for SSH host keys...")
        if not os.path.exists('/etc/ssh/ssh_host_ed25519_key'):
            print("SSH host keys not found. Generating new host keys...")
            subprocess.run(['ssh-keygen', '-t', 'ed25519', '-f', '/etc/ssh/ssh_host_ed25519_key', '-N', '""'], check=True)
            subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-f', '/etc/ssh/ssh_host_rsa_key', '-N', '""'], check=True)
            print("SSH host keys generated successfully.")
        else:
            print("SSH host keys are already present.")

        # Check if PUBLIC_KEY is set
        public_key = os.environ.get('PUBLIC_KEY', '').strip()

        if public_key:
            # Ensure the .ssh directory exists
            os.makedirs('/root/.ssh', exist_ok=True)

            # Add the public key to authorized_keys
            with open('/root/.ssh/authorized_keys', 'w') as f:
                f.write(public_key + '\n')

            # Set correct permissions
            os.chmod('/root/.ssh', 0o700)
            os.chmod('/root/.ssh/authorized_keys', 0o600)

        print("SSH Configuration Updated.")

        return True
    except Exception as e:
        print(f"Error setting up SSH: {str(e)}")
        return False
