"""ShopSystem: achat/vente."""

import json
import logging
import os
from game.features.inventory.components import InventoryComponent

logger = logging.getLogger(__name__)


_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_shop_config() -> dict:
    with open(os.path.join(_DATA_DIR, "shop_config.json"), "r") as f:
        return json.load(f)


def try_purchase(inventory: InventoryComponent, trade_index: int = 0) -> bool:
    config = load_shop_config()
    trades = config.get("trades", [])
    if trade_index >= len(trades):
        return False

    trade = trades[trade_index]
    cost_item = trade["cost_item"]
    cost_amount = trade["cost_amount"]
    reward_item = trade["reward_item"]

    if inventory.count(cost_item) >= cost_amount:
        for _ in range(cost_amount):
            inventory.remove_item(cost_item)
        inventory.add_item(reward_item)
        logger.info("Achat réussi: %dx %s → %s", cost_amount, cost_item, reward_item)
        return True
    logger.debug("Achat échoué: pas assez de %s (%d/%d)", cost_item, inventory.count(cost_item), cost_amount)
    return False
