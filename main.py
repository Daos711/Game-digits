#!/usr/bin/env python3
"""Точка входа для игры 'Игра цифры'."""

from game_digits.app import GameApp


def main():
    app = GameApp()
    app.run()


if __name__ == "__main__":
    main()
