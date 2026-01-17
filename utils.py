import yaml

def load_config():
    """Reads the YAML file so the script knows the URL and credentials."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: config.yaml file not found!")
        return None

def mock_ssh(host="10.1.1.1"):
    """Mock placeholder for SSH connection as requested."""
    print(f"MOCK_SSH: Connecting to host {host}...")

def mock_rdp(host="10.1.1.1"):
    """Mock placeholder for RDP validation as requested."""
    print(f"MOCK_RDP: Validating remote connection for {host}...")
