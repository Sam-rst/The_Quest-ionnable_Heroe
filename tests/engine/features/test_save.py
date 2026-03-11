"""Tests pour engine.features.save."""

import json
from unittest.mock import patch
from engine.features.save.logic import SaveManager
from engine.features.save.json_backend import JsonBackend


class TestJsonBackend:
    def test_save_and_load_round_trip(self, tmp_path):
        path = str(tmp_path / "test.json")
        backend = JsonBackend(path)
        backend.save({"key": "value", "count": 42})
        data = backend.load()
        assert data == {"key": "value", "count": 42}

    def test_load_missing_file(self, tmp_path):
        path = str(tmp_path / "missing.json")
        backend = JsonBackend(path)
        assert backend.load() == {}

    def test_load_corrupted_json(self, tmp_path):
        path = str(tmp_path / "bad.json")
        with open(path, "w") as f:
            f.write("{not valid json")
        backend = JsonBackend(path)
        assert backend.load() == {}

    def test_delete(self, tmp_path):
        path = str(tmp_path / "test.json")
        backend = JsonBackend(path)
        backend.save({"x": 1})
        assert backend.exists()
        backend.delete()
        assert not backend.exists()

    def test_exists_true(self, tmp_path):
        path = str(tmp_path / "test.json")
        backend = JsonBackend(path)
        backend.save({"x": 1})
        assert backend.exists()

    def test_exists_false(self, tmp_path):
        path = str(tmp_path / "nope.json")
        backend = JsonBackend(path)
        assert not backend.exists()

    def test_save_creates_directories(self, tmp_path):
        path = str(tmp_path / "sub" / "dir" / "test.json")
        backend = JsonBackend(path)
        backend.save({"nested": True})
        assert backend.load() == {"nested": True}

    def test_save_os_error(self, tmp_path):
        path = str(tmp_path / "test.json")
        backend = JsonBackend(path)
        with patch("builtins.open", side_effect=OSError("disk full")):
            backend.save({"x": 1})  # should not raise, just log


class TestSaveManager:
    def test_get_and_set(self, tmp_path):
        path = str(tmp_path / "save.json")
        backend = JsonBackend(path)
        sm = SaveManager(backend)
        sm.set("name", "Hero")
        assert sm.get("name") == "Hero"

    def test_get_default(self, tmp_path):
        path = str(tmp_path / "save.json")
        backend = JsonBackend(path)
        sm = SaveManager(backend)
        assert sm.get("missing", "fallback") == "fallback"

    def test_lazy_load(self, tmp_path):
        path = str(tmp_path / "save.json")
        backend = JsonBackend(path)
        backend.save({"existing": True})
        sm = SaveManager(backend)
        assert sm.get("existing") is True

    def test_save_and_reload_round_trip(self, tmp_path):
        path = str(tmp_path / "save.json")
        backend = JsonBackend(path)
        sm = SaveManager(backend)
        sm.set("hp", 100)
        sm.save()
        sm.reload()
        assert sm.get("hp") == 100

    def test_delete(self, tmp_path):
        path = str(tmp_path / "save.json")
        backend = JsonBackend(path)
        sm = SaveManager(backend)
        sm.set("x", 1)
        sm.save()
        sm.delete()
        assert not backend.exists()
        assert sm.get("x") is None

    def test_empty_backend(self, tmp_path):
        path = str(tmp_path / "empty.json")
        backend = JsonBackend(path)
        sm = SaveManager(backend)
        assert sm.data == {}

    def test_complex_data(self, tmp_path):
        path = str(tmp_path / "save.json")
        backend = JsonBackend(path)
        sm = SaveManager(backend)
        sm.set("inventory", ["sword", "shield"])
        sm.set("stats", {"hp": 100, "mp": 50})
        sm.save()
        sm.reload()
        assert sm.get("inventory") == ["sword", "shield"]
        assert sm.get("stats")["hp"] == 100
