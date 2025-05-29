import os
import json
from pathlib import Path


def get_config_path() -> Path:
    # Determine config file path from env or default
    return Path(os.environ.get('GITBRIDGE_CONFIG', Path.home() / '.gitbridge' / 'config.json'))

class Config:
    def __init__(self, path: Path, data: dict):
        self.path = path
        self.data = data

    @classmethod
    def load(cls) -> 'Config':
        path = get_config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            data = {"accounts": {}}
        return cls(path, data)

    def save(self) -> None:
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)
