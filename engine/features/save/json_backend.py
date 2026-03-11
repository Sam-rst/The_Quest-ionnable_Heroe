"""JSON backend for the SaveManager."""

import json
import os
from engine.features.save.logic import SaveBackend


class JsonBackend(SaveBackend):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def load(self) -> dict:
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self, data: dict) -> None:
        os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def delete(self) -> None:
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def exists(self) -> bool:
        return os.path.exists(self.filepath)
