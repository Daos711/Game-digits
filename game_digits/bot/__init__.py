"""
Bot module for automated game playing.

This module will contain the AI bot that can play the game optimally.
"""

from game_digits.bot.bot import Bot
from game_digits.bot.strategy import Strategy, GreedyStrategy, OptimalStrategy

__all__ = ['Bot', 'Strategy', 'GreedyStrategy', 'OptimalStrategy']
