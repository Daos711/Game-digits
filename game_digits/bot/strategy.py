"""
Strategy classes for bot decision making.

GAME MECHANICS SUMMARY (for future reference):
==============================================

The game is played on a 13x13 grid with numbered tiles (1-9).
Goal: Remove all pairs of identical tiles by clicking them in sequence.

SCORING SYSTEM:
- When two identical tiles are removed, points are awarded based on
  the Manhattan distance between them:
  - Distance 1: +1 point
  - Distance 2: +1+2 = +3 points
  - Distance 3: +1+2+3 = +6 points
  - Distance N: sum(1..N) = N*(N+1)/2 points
  Formula: score = distance * (distance + 1) / 2

- Moving a tile COSTS points:
  - Each cell moved deducts 1 point per cell
  - Moving 3 cells = -3 points

OPTIMAL STRATEGY CONSIDERATIONS:
- Farther pairs yield more points (quadratic growth)
- But moving tiles to create distance costs points (linear cost)
- Sometimes it's better to remove close pairs immediately
- Sometimes it's better to move tiles apart first, then remove

EXAMPLE:
- Two tiles at distance 2: immediate removal = +3 points
- Move one tile 3 cells to make distance 5, then remove:
  - Movement cost: -3 points
  - Removal reward: +15 points (5*6/2)
  - Net gain: +12 points vs +3 = +9 profit

BOT MODES:
1. GreedyStrategy - always removes the highest-scoring pair available now
2. OptimalStrategy - looks ahead to find the best sequence of moves

COMPETITION MODE (future):
- Bot and player take turns
- Or bot plays separately and scores are compared
- Could add time pressure for fair comparison
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game_digits.game import Game
    from game_digits.sprites import Tile


class Move:
    """Represents a single move in the game.

    A move can be either:
    - Removing a pair of tiles (tile1, tile2, move_tile=None)
    - Moving a tile then removing (tile1, tile2, move_tile, direction, distance)
    """

    def __init__(
        self,
        tile1_pos: Tuple[int, int],
        tile2_pos: Tuple[int, int],
        move_tile_pos: Optional[Tuple[int, int]] = None,
        move_direction: Optional[str] = None,
        move_distance: int = 0
    ):
        """
        Args:
            tile1_pos: Position (row, col) of first tile to remove
            tile2_pos: Position (row, col) of second tile to remove
            move_tile_pos: If moving before removal, which tile to move
            move_direction: Direction to move ('up', 'down', 'left', 'right')
            move_distance: How many cells to move
        """
        self.tile1_pos = tile1_pos
        self.tile2_pos = tile2_pos
        self.move_tile_pos = move_tile_pos
        self.move_direction = move_direction
        self.move_distance = move_distance

    @property
    def is_direct_removal(self) -> bool:
        """True if this is a simple removal without movement."""
        return self.move_tile_pos is None

    def calculate_score(self) -> int:
        """Calculate net score change from this move.

        Returns:
            Net points gained (removal reward minus movement cost)
        """
        # Calculate Manhattan distance after potential movement
        r1, c1 = self.tile1_pos
        r2, c2 = self.tile2_pos

        # If we're moving a tile, adjust its position
        if self.move_tile_pos and self.move_direction:
            if self.move_tile_pos == self.tile1_pos:
                r1, c1 = self._apply_movement(r1, c1)
            else:
                r2, c2 = self._apply_movement(r2, c2)

        distance = abs(r1 - r2) + abs(c1 - c2)
        removal_score = distance * (distance + 1) // 2
        movement_cost = self.move_distance

        return removal_score - movement_cost

    def _apply_movement(self, row: int, col: int) -> Tuple[int, int]:
        """Apply movement to a position."""
        if self.move_direction == 'up':
            return row - self.move_distance, col
        elif self.move_direction == 'down':
            return row + self.move_distance, col
        elif self.move_direction == 'left':
            return row, col - self.move_distance
        elif self.move_direction == 'right':
            return row, col + self.move_distance
        return row, col

    def __repr__(self) -> str:
        if self.is_direct_removal:
            return f"Move(remove {self.tile1_pos} + {self.tile2_pos})"
        return (f"Move(move {self.move_tile_pos} {self.move_direction} {self.move_distance}, "
                f"then remove {self.tile1_pos} + {self.tile2_pos})")


class Strategy(ABC):
    """Abstract base class for bot strategies.

    Subclasses must implement find_best_move() to determine
    the optimal action given the current game state.
    """

    @abstractmethod
    def find_best_move(self, game: 'Game') -> Optional[Move]:
        """Find the best move for the current game state.

        Args:
            game: Current game instance with board state

        Returns:
            Best Move to make, or None if no valid moves exist
        """
        pass

    def find_all_pairs(self, game: 'Game') -> List[Tuple['Tile', 'Tile']]:
        """Find all pairs of identical tiles on the board.

        Args:
            game: Current game instance

        Returns:
            List of (tile1, tile2) tuples for matching pairs
        """
        # TODO: Implement - scan board for matching tile values
        pass

    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class GreedyStrategy(Strategy):
    """Greedy strategy: always pick the highest-scoring immediate move.

    This strategy does not consider movement - it only looks at
    pairs that can be removed right now and picks the one with
    the highest distance (and thus highest score).

    Pros:
    - Simple and fast
    - Good baseline performance

    Cons:
    - Misses opportunities where movement + removal yields more
    - Can get stuck in suboptimal local maxima
    """

    def find_best_move(self, game: 'Game') -> Optional[Move]:
        """Find the pair with maximum distance for immediate removal.

        Args:
            game: Current game instance

        Returns:
            Move for the best immediate pair, or None
        """
        # TODO: Implement
        # 1. Find all pairs of identical tiles
        # 2. Calculate distance for each pair
        # 3. Return Move for the pair with max distance
        pass


class OptimalStrategy(Strategy):
    """Optimal strategy: considers movement to maximize total score.

    This strategy evaluates whether moving tiles before removal
    can yield a higher net score (removal reward - movement cost).

    Algorithm outline:
    1. For each pair of identical tiles:
       a. Calculate immediate removal score
       b. For each possible movement of either tile:
          - Calculate new distance after movement
          - Calculate net score (new removal score - movement cost)
       c. Track the best option (immediate or with movement)
    2. Return the globally best move

    Optimization considerations:
    - Movement is only profitable if it increases distance enough
    - For movement of N cells, need distance increase > N to profit
    - Can prune moves that clearly won't be profitable

    Future improvements:
    - Look multiple moves ahead (minimax/alpha-beta for competition)
    - Consider board state after removal (new pairs that form)
    - Factor in time pressure (faster decisions under time limit)
    """

    def __init__(self, max_movement_distance: int = 5):
        """
        Args:
            max_movement_distance: Maximum cells to consider moving
                                   (limits search space)
        """
        self.max_movement_distance = max_movement_distance

    def find_best_move(self, game: 'Game') -> Optional[Move]:
        """Find the move that maximizes net score gain.

        Considers both immediate removals and movement + removal.

        Args:
            game: Current game instance

        Returns:
            Optimal Move, or None if no valid moves
        """
        # TODO: Implement
        # 1. Find all pairs
        # 2. For each pair, evaluate:
        #    - Immediate removal score
        #    - All possible movements and their net scores
        # 3. Return the move with highest net score
        pass

    def _evaluate_movements(
        self,
        game: 'Game',
        tile: 'Tile',
        partner: 'Tile'
    ) -> List[Move]:
        """Generate all possible movement options for a tile.

        Args:
            game: Current game instance
            tile: Tile to potentially move
            partner: The matching tile (for pair removal)

        Returns:
            List of possible Moves involving movement of tile
        """
        # TODO: Implement
        # For each direction (up, down, left, right):
        #   For each distance (1 to max_movement_distance):
        #     If movement is valid (no obstacles):
        #       Create Move and calculate score
        pass
