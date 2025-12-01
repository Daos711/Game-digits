"""
Bot class for automated game playing.

OVERVIEW:
=========
The Bot class provides an AI player that can play the game automatically.
It uses a Strategy to determine the best moves and can operate in different modes.

USAGE MODES:
============

1. DEMO MODE (bot plays alone):
   - Bot plays the game while user watches
   - Useful for demonstrating optimal play
   - Can adjust speed of play for visibility

2. COMPETITION MODE (bot vs player):
   Option A - Turn-based:
     - Player and bot alternate turns
     - Each removes one pair per turn
     - Higher total score wins

   Option B - Parallel play:
     - Same initial board state
     - Player plays normally
     - Bot plays separately (simulated)
     - Compare final scores

3. HINT MODE:
   - Bot suggests the best move to player
   - Player can accept or ignore suggestion
   - Educational mode to learn optimal strategy

IMPLEMENTATION NOTES:
=====================
- Bot operates on a copy of game state (doesn't modify real game directly)
- For competition mode, need to sync bot actions with game display
- Animation speed should be configurable for watchability
- Consider adding "explain move" feature for learning

FUTURE ENHANCEMENTS:
====================
- Difficulty levels (limit how far ahead bot looks)
- Personality modes (aggressive, conservative, balanced)
- Learning mode (bot improves by watching player)
- Replay analysis (bot comments on player's moves)
"""

from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from game_digits.bot.strategy import Strategy, GreedyStrategy, OptimalStrategy, Move

if TYPE_CHECKING:
    from game_digits.game import Game


class BotMode(Enum):
    """Operating modes for the bot."""
    DEMO = "demo"           # Bot plays alone for demonstration
    COMPETITION = "competition"  # Bot competes against player
    HINT = "hint"           # Bot provides move suggestions


class BotState(Enum):
    """Current state of bot execution."""
    IDLE = "idle"           # Not currently playing
    THINKING = "thinking"   # Calculating next move
    MOVING = "moving"       # Executing a tile movement
    REMOVING = "removing"   # Executing a pair removal
    WAITING = "waiting"     # Waiting for animation to complete
    FINISHED = "finished"   # Game completed


class Bot:
    """AI player that can play the game automatically.

    The bot analyzes the game state and makes optimal (or near-optimal)
    decisions based on its strategy. It can operate in different modes
    for demonstration, competition, or assistance.

    Attributes:
        strategy: The Strategy instance used for decision making
        mode: Current operating mode (demo, competition, hint)
        state: Current execution state
        move_delay: Milliseconds between moves (for visibility)
        current_move: The move currently being executed
    """

    def __init__(
        self,
        strategy: Optional[Strategy] = None,
        mode: BotMode = BotMode.DEMO,
        move_delay: int = 500
    ):
        """Initialize the bot.

        Args:
            strategy: Strategy to use (defaults to OptimalStrategy)
            mode: Operating mode
            move_delay: Delay between moves in milliseconds
        """
        self.strategy = strategy or OptimalStrategy()
        self.mode = mode
        self.state = BotState.IDLE
        self.move_delay = move_delay
        self.current_move: Optional[Move] = None
        self._move_queue: List[Move] = []
        self._last_move_time = 0
        self._game_snapshot = None  # For competition mode

    def start(self, game: 'Game') -> None:
        """Start the bot playing on the given game.

        Args:
            game: Game instance to play on
        """
        self.state = BotState.THINKING
        self._game_snapshot = None
        self._move_queue.clear()
        # TODO: Begin analysis

    def stop(self) -> None:
        """Stop the bot from playing."""
        self.state = BotState.IDLE
        self.current_move = None
        self._move_queue.clear()

    def update(self, game: 'Game', current_time: int) -> Optional[Move]:
        """Update bot state and return action if ready.

        Should be called each frame. Returns a Move when the bot
        is ready to make a move, or None if waiting/thinking.

        Args:
            game: Current game state
            current_time: Current time in milliseconds (pygame.time.get_ticks())

        Returns:
            Move to execute, or None if not ready
        """
        if self.state == BotState.IDLE or self.state == BotState.FINISHED:
            return None

        if self.state == BotState.WAITING:
            # Check if enough time has passed since last move
            if current_time - self._last_move_time >= self.move_delay:
                self.state = BotState.THINKING

        if self.state == BotState.THINKING:
            # Find next move
            move = self.strategy.find_best_move(game)
            if move is None:
                # No valid moves - game might be over or stuck
                self.state = BotState.FINISHED
                return None

            self.current_move = move
            self._last_move_time = current_time

            if move.is_direct_removal:
                self.state = BotState.REMOVING
            else:
                self.state = BotState.MOVING

            return move

        return None

    def get_hint(self, game: 'Game') -> Optional[Move]:
        """Get a hint for the best move without executing it.

        Args:
            game: Current game state

        Returns:
            Suggested Move, or None if no valid moves
        """
        return self.strategy.find_best_move(game)

    def explain_move(self, move: Move) -> str:
        """Generate human-readable explanation for a move.

        Args:
            move: Move to explain

        Returns:
            String explanation of why this move is good
        """
        score = move.calculate_score()

        if move.is_direct_removal:
            r1, c1 = move.tile1_pos
            r2, c2 = move.tile2_pos
            distance = abs(r1 - r2) + abs(c1 - c2)
            return (
                f"Удалить пару на расстоянии {distance}. "
                f"Награда: +{score} очков."
            )
        else:
            return (
                f"Переместить плитку {move.move_tile_pos} "
                f"{move.move_direction} на {move.move_distance} клеток, "
                f"затем удалить пару. "
                f"Чистая прибыль: +{score} очков."
            )

    def set_difficulty(self, level: str) -> None:
        """Adjust bot difficulty.

        Args:
            level: 'easy', 'medium', or 'hard'
        """
        if level == 'easy':
            # Use greedy strategy (no lookahead)
            self.strategy = GreedyStrategy()
        elif level == 'medium':
            # Optimal but with limited movement consideration
            self.strategy = OptimalStrategy(max_movement_distance=3)
        else:  # hard
            # Full optimal strategy
            self.strategy = OptimalStrategy(max_movement_distance=6)

    @property
    def is_playing(self) -> bool:
        """Check if bot is currently active."""
        return self.state not in (BotState.IDLE, BotState.FINISHED)

    def get_statistics(self) -> dict:
        """Get bot performance statistics.

        Returns:
            Dict with stats like moves_made, total_score, avg_score_per_move
        """
        # TODO: Track and return statistics
        return {
            'moves_made': 0,
            'total_score': 0,
            'avg_score_per_move': 0.0,
            'movement_cells': 0,
            'pairs_removed': 0
        }
