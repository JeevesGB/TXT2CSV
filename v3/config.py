import json
import os
from utils import resource_path

CONFIG_FILE = "data/config.json"

def load_config():
    path = resource_path(CONFIG_FILE)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_config(cfg):
    path = resource_path(CONFIG_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)
