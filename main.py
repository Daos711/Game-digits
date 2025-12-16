#!/usr/bin/env python3
"""Точка входа для игры 'Игра цифры'."""

import sys
import pygame


def main():
    # Check for test mode flag
    test_mode = "--test" in sys.argv or "-t" in sys.argv

    while True:
        if test_mode:
            from game_digits.test_app import TestGameApp
            app = TestGameApp()
        else:
            from game_digits.app import GameApp
            app = GameApp()

        result = app.run()

        if result == 'restart':
            # Settings changed - reinitialize
            pygame.quit()
            # Recalculate scaled values
            from game_digits import scale
            scale.recalculate()
            # Reimport constants that depend on scale
            from game_digits import constants
            constants.recalculate()
        else:
            break


if __name__ == "__main__":
    main()
