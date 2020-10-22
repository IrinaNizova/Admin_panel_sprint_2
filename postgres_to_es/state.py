import json
import logging
from typing import Optional


class JsonFileStorage:
    def __init__(self, file_path: Optional[str] = 'last_time.json'):
        self.file_path = file_path

    def save_state(self, key, value) -> None:
        if self.file_path is None:
            return
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            data[key] = value
        with open(self.file_path, 'w') as f:
            f.write(json.dumps(data))

    def get_state(self, key) -> dict:
        if self.file_path is None:
            logging.info('No state file provided.')
            return {}
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

            return data[key]

        except FileNotFoundError:
            pass
