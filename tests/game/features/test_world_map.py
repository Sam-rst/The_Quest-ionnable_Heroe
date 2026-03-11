"""Tests pour game.features.world_map."""

from engine.core.game import Game
from game.features.world_map import logic as wm_logic
from game.features.world_map.logic import load_maps_config, load_spawns_config, WorldMapSystem


class TestLoadMapsConfig:
    def test_returns_dict(self):
        config = load_maps_config()
        assert isinstance(config, dict)

    def test_missing_file_returns_empty(self, monkeypatch, tmp_path):
        monkeypatch.setattr(wm_logic, "_DATA_DIR", str(tmp_path))
        config = load_maps_config()
        assert config == {}

    def test_corrupted_file_returns_empty(self, monkeypatch, tmp_path):
        path = tmp_path / "maps.json"
        path.write_text("{bad json")
        monkeypatch.setattr(wm_logic, "_DATA_DIR", str(tmp_path))
        config = load_maps_config()
        assert config == {}


class TestLoadSpawnsConfig:
    def test_returns_dict(self):
        config = load_spawns_config()
        assert isinstance(config, dict)

    def test_missing_file_returns_empty(self, monkeypatch, tmp_path):
        monkeypatch.setattr(wm_logic, "_DATA_DIR", str(tmp_path))
        config = load_spawns_config()
        assert config == {}

    def test_corrupted_file_returns_empty(self, monkeypatch, tmp_path):
        path = tmp_path / "spawns.json"
        path.write_text("{bad")
        monkeypatch.setattr(wm_logic, "_DATA_DIR", str(tmp_path))
        config = load_spawns_config()
        assert config == {}


class TestWorldMapSystem:
    def test_current_map_default(self):
        game = Game()
        wms = WorldMapSystem()
        game.add_system(wms)
        assert wms.current_map == "Overworld"

    def test_get_bg_color_known(self):
        game = Game()
        wms = WorldMapSystem()
        game.add_system(wms)
        # The actual maps.json should have Overworld
        color = wms.get_bg_color("Overworld")
        assert isinstance(color, str)

    def test_get_bg_color_unknown(self):
        game = Game()
        wms = WorldMapSystem()
        game.add_system(wms)
        color = wms.get_bg_color("NonExistentMap")
        assert color == "#71ddee"
