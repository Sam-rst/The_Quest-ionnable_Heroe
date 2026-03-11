"""Tests pour engine.features.tilemap."""

from engine.features.tilemap.logic import TileRect, Waypoint, TeleporterData, TilemapData


class TestTileRect:
    def test_creation(self):
        r = TileRect(x=10, y=20, width=30, height=40)
        assert r.x == 10
        assert r.width == 30


class TestWaypoint:
    def test_creation(self):
        w = Waypoint(name="Spawn", x=100, y=200)
        assert w.name == "Spawn"
        assert w.x == 100


class TestTeleporterData:
    def test_creation(self):
        t = TeleporterData(name="tp1", destination_map="Dungeon",
                           destination_waypoint="Entry", x=0, y=0, width=64, height=64)
        assert t.destination_map == "Dungeon"


class TestTilemapData:
    def test_pixel_width_height(self):
        tm = TilemapData(name="test", width_tiles=10, height_tiles=8,
                         tile_width=16, tile_height=16, scale=4)
        assert tm.pixel_width == 10 * 16 * 4
        assert tm.pixel_height == 8 * 16 * 4

    def test_scaled_tile_width(self):
        tm = TilemapData(name="test", width_tiles=1, height_tiles=1,
                         tile_width=16, tile_height=16, scale=4)
        assert tm.scaled_tile_width == 64
        assert tm.scaled_tile_height == 64

    def test_get_waypoint_found(self):
        tm = TilemapData(name="test", width_tiles=1, height_tiles=1,
                         tile_width=16, tile_height=16, scale=4,
                         waypoints=[Waypoint("Spawn", 10, 20)])
        result = tm.get_waypoint("Spawn")
        assert result == (40, 80)

    def test_get_waypoint_not_found(self):
        tm = TilemapData(name="test", width_tiles=1, height_tiles=1,
                         tile_width=16, tile_height=16, scale=4)
        assert tm.get_waypoint("Missing") is None

    def test_defaults_empty_lists(self):
        tm = TilemapData(name="test", width_tiles=1, height_tiles=1,
                         tile_width=16, tile_height=16)
        assert tm.collision_rects == []
        assert tm.waypoints == []
        assert tm.teleporters == []
