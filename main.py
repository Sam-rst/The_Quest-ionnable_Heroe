"""The Quest-ionnable Heroe — Point d'entrée."""

import argparse
import logging
import sys

from engine.core.logging_setup import setup_logging
from game.app import create_game

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Quest-ionnable Heroe")
    parser.add_argument("--debug", action="store_true", help="Active les logs DEBUG + overlay")
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=level)

    try:
        create_game(debug=args.debug)
    except Exception:
        logger.exception("Erreur fatale — arrêt du jeu")
        try:
            import pygame
            pygame.quit()
        except Exception:
            pass
        sys.exit(1)
