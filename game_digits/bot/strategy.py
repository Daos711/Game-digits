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

    def calculate_score(self, after_move_distance: int = None) -> int:
        """Calculate net score change from this move.

        Args:
            after_move_distance: Distance after movement (if pre-calculated)

        Returns:
            Net points gained (removal reward minus movement cost)
        """
        if after_move_distance is not None:
            distance = after_move_distance
        else:
            r1, c1 = self.tile1_pos
            r2, c2 = self.tile2_pos

            if self.move_tile_pos and self.move_direction:
                if self.move_tile_pos == self.tile1_pos:
                    r1, c1 = self._apply_movement(r1, c1)
                else:
                    r2, c2 = self._apply_movement(r2, c2)

            distance = abs(r1 - r2) + abs(c1 - c2)

        # Формула из game.py: (d + 1) * (d + 2) // 2
        removal_score = (distance + 1) * (distance + 2) // 2
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

    def can_remove_pair(self, game: 'Game', tile1: 'Tile', tile2: 'Tile') -> bool:
        """Check if two tiles can be removed (same line, clear path)."""
        if tile1.is_moving or tile2.is_moving:
            return False

        x1, y1 = tile1.position
        x2, y2 = tile2.position

        # Must match: same number or sum to 10
        if tile1.number != tile2.number and tile1.number + tile2.number != 10:
            return False

        # Must be on same line
        if x1 == x2:  # Same row (horizontal line)
            # Check path is clear
            min_y, max_y = min(y1, y2), max(y1, y2)
            if max_y - min_y == 1:
                return True  # Adjacent
            for j in range(min_y + 1, max_y):
                if game.board[x1][j] is not None:
                    return False
            return True
        elif y1 == y2:  # Same column (vertical line)
            min_x, max_x = min(x1, x2), max(x1, x2)
            if max_x - min_x == 1:
                return True  # Adjacent
            for i in range(min_x + 1, max_x):
                if game.board[i][y1] is not None:
                    return False
            return True

        return False  # Not on same line

    def find_all_removable_pairs(self, game: 'Game') -> List[Tuple['Tile', 'Tile', int]]:
        """Find all pairs that can be removed right now.

        Returns:
            List of (tile1, tile2, distance) tuples
        """
        pairs = []
        tiles = [t for t in game.tiles if not t.is_moving]

        for i, tile1 in enumerate(tiles):
            for tile2 in tiles[i + 1:]:
                if self.can_remove_pair(game, tile1, tile2):
                    x1, y1 = tile1.position
                    x2, y2 = tile2.position
                    distance = abs(x1 - x2) + abs(y1 - y2)
                    pairs.append((tile1, tile2, distance))

        return pairs

    def find_matching_tiles(self, game: 'Game') -> List[Tuple['Tile', 'Tile']]:
        """Find all pairs of tiles that could match (same number or sum=10)."""
        pairs = []
        tiles = [t for t in game.tiles if not t.is_moving]

        for i, tile1 in enumerate(tiles):
            for tile2 in tiles[i + 1:]:
                if tile1.number == tile2.number or tile1.number + tile2.number == 10:
                    pairs.append((tile1, tile2))

        return pairs

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
        pairs = self.find_all_removable_pairs(game)

        if not pairs:
            return None

        # Find pair with maximum score
        best_pair = None
        best_score = -1

        for tile1, tile2, distance in pairs:
            score = (distance + 1) * (distance + 2) // 2
            if score > best_score:
                best_score = score
                best_pair = (tile1, tile2)

        if best_pair:
            return Move(best_pair[0].position, best_pair[1].position)

        return None


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

    def __init__(self, max_movement_distance: int = 10):
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
        best_move = None
        best_score = -float('inf')

        # 1. Check all immediate removals
        for tile1, tile2, distance in self.find_all_removable_pairs(game):
            score = (distance + 1) * (distance + 2) // 2
            if score > best_score:
                best_score = score
                best_move = Move(tile1.position, tile2.position)

        # 2. Check all matching pairs (even if not currently removable)
        for tile1, tile2 in self.find_matching_tiles(game):
            # Try moving tile1 to align with tile2
            moves1 = self._evaluate_movements(game, tile1, tile2)
            for move, score in moves1:
                if score > best_score:
                    best_score = score
                    best_move = move

            # Try moving tile2 to align with tile1
            moves2 = self._evaluate_movements(game, tile2, tile1)
            for move, score in moves2:
                if score > best_score:
                    best_score = score
                    best_move = move

        return best_move

    def _evaluate_movements(
        self,
        game: 'Game',
        tile: 'Tile',
        partner: 'Tile'
    ) -> List[Tuple[Move, int]]:
        """Generate all possible movement options for a tile.

        Args:
            game: Current game instance
            tile: Tile to potentially move
            partner: The matching tile (for pair removal)

        Returns:
            List of (Move, score) tuples
        """
        moves = []
        board_size = len(game.board)
        r1, c1 = tile.position
        r2, c2 = partner.position

        directions = [
            ('up', -1, 0),
            ('down', 1, 0),
            ('left', 0, -1),
            ('right', 0, 1)
        ]

        for dir_name, dr, dc in directions:
            for dist in range(1, self.max_movement_distance + 1):
                new_r = r1 + dr * dist
                new_c = c1 + dc * dist

                # Check bounds
                if not (0 <= new_r < board_size and 0 <= new_c < board_size):
                    break  # Can't go further in this direction

                # Check path is clear (all cells between current and target)
                path_clear = True
                for step in range(1, dist + 1):
                    check_r = r1 + dr * step
                    check_c = c1 + dc * step
                    cell = game.board[check_r][check_c]
                    if cell is not None and cell != tile and cell != partner:
                        path_clear = False
                        break

                if not path_clear:
                    break  # Can't go further

                # After movement, can we remove the pair?
                # They must be on same line with clear path
                if new_r == r2:  # Same row after movement
                    # Check path between new position and partner
                    min_c, max_c = min(new_c, c2), max(new_c, c2)
                    clear = True
                    for j in range(min_c + 1, max_c):
                        cell = game.board[new_r][j]
                        if cell is not None and cell != tile and cell != partner:
                            clear = False
                            break
                    if clear:
                        new_distance = abs(new_c - c2)
                        removal_score = (new_distance + 1) * (new_distance + 2) // 2
                        net_score = removal_score - dist
                        move = Move(
                            tile1_pos=tile.position,
                            tile2_pos=partner.position,
                            move_tile_pos=tile.position,
                            move_direction=dir_name,
                            move_distance=dist
                        )
                        moves.append((move, net_score))

                elif new_c == c2:  # Same column after movement
                    # Check path between new position and partner
                    min_r, max_r = min(new_r, r2), max(new_r, r2)
                    clear = True
                    for i in range(min_r + 1, max_r):
                        cell = game.board[i][new_c]
                        if cell is not None and cell != tile and cell != partner:
                            clear = False
                            break
                    if clear:
                        new_distance = abs(new_r - r2)
                        removal_score = (new_distance + 1) * (new_distance + 2) // 2
                        net_score = removal_score - dist
                        move = Move(
                            tile1_pos=tile.position,
                            tile2_pos=partner.position,
                            move_tile_pos=tile.position,
                            move_direction=dir_name,
                            move_distance=dist
                        )
                        moves.append((move, net_score))

        return moves
