import json
import os

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"✓ Config loaded from {config_file}")
            return config
        else:
            print(f"Config file {config_file} not found. Creating default config.")
            return create_default_config(config_file)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def save_config(config, config_file='config.json'):
    """Save configuration to JSON file"""
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✓ Config saved to {config_file}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def create_default_config(config_file='config.json'):
    """Create default configuration file"""
    default_config = {
        "client_id": "YOUR_CLIENT_ID",
        "access_token": "YOUR_ACCESS_TOKEN",
        "symbol": "NSE:SBIN-EQ",
        "quantity": 1
    }
    save_config(default_config, config_file)
    return default_config