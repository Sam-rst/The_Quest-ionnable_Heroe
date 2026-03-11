"""Tests pour game.features.shop."""

import json
import os
from game.features.inventory.components import InventoryComponent
from game.features.shop import logic as shop_logic
from game.features.shop.logic import load_shop_config, try_purchase


class TestLoadShopConfig:
    def test_returns_dict(self):
        config = load_shop_config()
        assert isinstance(config, dict)

    def test_missing_file_returns_default(self, monkeypatch, tmp_path):
        monkeypatch.setattr(shop_logic, "_DATA_DIR", str(tmp_path))
        config = load_shop_config()
        assert config == {"trades": []}

    def test_corrupted_file_returns_default(self, monkeypatch, tmp_path):
        path = tmp_path / "shop_config.json"
        path.write_text("{bad json")
        monkeypatch.setattr(shop_logic, "_DATA_DIR", str(tmp_path))
        config = load_shop_config()
        assert config == {"trades": []}


class TestTryPurchase:
    def test_success(self, monkeypatch, tmp_path):
        config = {"trades": [{"cost_item": "Piece", "cost_amount": 3,
                               "reward_item": "Potion", "display": "3 Pieces → 1 Potion"}]}
        path = tmp_path / "shop_config.json"
        path.write_text(json.dumps(config))
        monkeypatch.setattr(shop_logic, "_DATA_DIR", str(tmp_path))

        inv = InventoryComponent()
        for _ in range(5):
            inv.add_item("Piece")
        result = try_purchase(inv, 0)
        assert result is True
        assert inv.count("Piece") == 2
        assert inv.count("Potion") == 1

    def test_not_enough_items(self, monkeypatch, tmp_path):
        config = {"trades": [{"cost_item": "Piece", "cost_amount": 10,
                               "reward_item": "Potion", "display": "10 Pieces → 1 Potion"}]}
        path = tmp_path / "shop_config.json"
        path.write_text(json.dumps(config))
        monkeypatch.setattr(shop_logic, "_DATA_DIR", str(tmp_path))

        inv = InventoryComponent()
        inv.add_item("Piece")
        result = try_purchase(inv, 0)
        assert result is False
        assert inv.count("Piece") == 1

    def test_invalid_trade_index(self, monkeypatch, tmp_path):
        config = {"trades": []}
        path = tmp_path / "shop_config.json"
        path.write_text(json.dumps(config))
        monkeypatch.setattr(shop_logic, "_DATA_DIR", str(tmp_path))

        inv = InventoryComponent()
        result = try_purchase(inv, 99)
        assert result is False

    def test_removes_correct_amount(self, monkeypatch, tmp_path):
        config = {"trades": [{"cost_item": "Piece", "cost_amount": 2,
                               "reward_item": "Potion", "display": "2 Pieces → 1 Potion"}]}
        path = tmp_path / "shop_config.json"
        path.write_text(json.dumps(config))
        monkeypatch.setattr(shop_logic, "_DATA_DIR", str(tmp_path))

        inv = InventoryComponent()
        for _ in range(4):
            inv.add_item("Piece")
        try_purchase(inv, 0)
        assert inv.count("Piece") == 2
