import json
import time
from datetime import datetime, timedelta
import requests




def save_dict_json(d, filename):
    """Save dictionary to JSON file"""
    with open(filename, 'w') as f:
        json.dump(d, f, indent=4)
    print(f"Saved to {filename}")

def load_dict_json(filename):
    """Load dictionary from JSON file"""
    with open(filename, 'r') as f:
        d = json.load(f)
    print(f"Loaded from {filename}")
    return d

config = load_dict_json("config.json")
access_token = config['access_token']

