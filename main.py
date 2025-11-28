#!/usr/bin/env python3
"""Точка входа для игры 'Игра цифры'."""

import sys


def main():
    # Check for test mode flag
    if "--test" in sys.argv or "-t" in sys.argv:
        from game_digits.test_app import TestGameApp
        app = TestGameApp()
    else:
        from game_digits.app import GameApp
        app = GameApp()

    app.run()


if __name__ == "__main__":
    main()
