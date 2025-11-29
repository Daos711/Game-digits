"""
Test game mode with minimal tiles for mechanics testing.
"""
import random
import pygame

from game_digits.constants import COLORS
from game_digits.sprites import Tile


# Test mode board size (same as main game for proper testing)
TEST_BOARD_SIZE = 10


class TestGame:
    """Simplified game with 6 tiles (3 pairs) for quick result window testing."""

    COUNTDOWN_EVENT = pygame.USEREVENT + 2
    TILE_APPEAR_EVENT = pygame.USEREVENT + 3

    def __init__(self, tiles, time_limit=60):
        self.tiles = tiles
        self.board = [[None for _ in range(TEST_BOARD_SIZE)] for _ in range(TEST_BOARD_SIZE)]
        self.score = 0
        self.time_limit = time_limit
        self.current_time = time_limit
        self.timer_started = False
        self.selected_tile = None
        self.original_color = None
        self.game_over_flag = False
        self.COLORS = COLORS
        self.prepare_to_end = False

        # Tile appearance animation state
        self.is_initializing = True
        self.tile_appear_delay = 50  # ms between tile appearances
        self.pending_tiles = []
        self.current_pattern_name = "test_pattern"
        self.prepare_tile_appearance()

    def prepare_tile_appearance(self):
        """Prepare 6 tiles (3 pairs) for animated appearance in center of board."""
        # Generate 3 pairs of numbers that sum to 10
        pairs = [
            (1, 9),
            (2, 8),
            (3, 7),
        ]

        # Create list of all numbers from pairs
        numbers = []
        for a, b in pairs:
            numbers.append(a)
            numbers.append(b)

        # Shuffle numbers
        random.shuffle(numbers)

        # Place tiles in center of 10x10 board (2 rows x 3 cols in center)
        # Center positions: rows 4-5, cols 3-5
        positions = [
            (4, 3), (4, 4), (4, 5),
            (5, 3), (5, 4), (5, 5),
        ]

        # Create pending tiles
        self.pending_tiles = []
        for i, pos in enumerate(positions):
            number = numbers[i]
            self.pending_tiles.append((pos, number))

    def start_tile_appearance(self):
        """Start the tile appearance animation timer."""
        pygame.time.set_timer(self.TILE_APPEAR_EVENT, self.tile_appear_delay)

    def spawn_next_tile(self):
        """Spawn the next tile in the appearance sequence."""
        if not self.pending_tiles:
            pygame.time.set_timer(self.TILE_APPEAR_EVENT, 0)
            self.is_initializing = False
            return None

        pos, number = self.pending_tiles.pop(0)
        row, col = pos
        tile = Tile(number, (row, col), COLORS[number])
        self.board[row][col] = tile
        self.tiles.add(tile)
        return tile

    def select_tile(self, tile):
        if self.selected_tile:
            self.selected_tile.update_color(self.original_color, (0, 0, 0))
        self.selected_tile = tile
        self.original_color = tile.color
        tile.update_color((255, 139, 2), (255, 255, 202))

    def deselect_tile(self):
        if self.selected_tile:
            self.selected_tile.update_color(self.original_color, (0, 0, 0))
            self.selected_tile = None
            self.original_color = None

    def remove_tiles(self, tile1, tile2):
        """Remove a pair of tiles if valid."""
        if tile1 is None or tile2 is None:
            return None
        if tile1.is_moving or tile2.is_moving:
            return None

        x1, y1 = tile1.position
        x2, y2 = tile2.position

        if tile1.number == tile2.number or tile1.number + tile2.number == 10:
            if x1 == x2:  # Same row
                if abs(y1 - y2) == 1 or all(
                    self.board[x1][j] is None for j in range(min(y1, y2) + 1, max(y1, y2))
                ):
                    self.score += (abs(y1 - y2) + 1) * (abs(y1 - y2) + 2) // 2
                    self.board[x1][y1] = None
                    self.board[x2][y2] = None
                    self.tiles.remove(tile1, tile2)
                    self.post_remove_actions()
                    step = 1 if y2 > y1 else -1
                    positions = [(x1, j) for j in range(y1, y2 + step, step)]
                    return positions
            elif y1 == y2:  # Same column
                if abs(x1 - x2) == 1 or all(
                    self.board[i][y1] is None for i in range(min(x1, x2) + 1, max(x1, x2))
                ):
                    self.score += (abs(x1 - x2) + 1) * (abs(x1 - x2) + 2) // 2
                    self.board[x1][y1] = None
                    self.board[x2][y2] = None
                    self.tiles.remove(tile1, tile2)
                    self.post_remove_actions()
                    step = 1 if x2 > x1 else -1
                    positions = [(i, y1) for i in range(x1, x2 + step, step)]
                    return positions
        return None

    def start_timer(self):
        if not self.timer_started:
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 1000)
            self.timer_started = True

    def stop_timer(self):
        if self.timer_started:
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 0)
            self.timer_started = False

    def handle_countdown(self):
        if self.current_time > 0:
            self.current_time -= 1
            if self.current_time == 0:
                self.game_over_flag = True
                self.stop_timer()
        else:
            self.game_over_flag = True

    def post_remove_actions(self):
        if not self.timer_started:
            self.start_timer()
        # Check if all tiles removed
        if not any(tile for row in self.board for tile in row):
            self.prepare_to_end = True
            self.stop_timer()

    def deduct_score(self, n):
        deduction = sum(range(1, n + 1))
        self.score = max(0, self.score - deduction)

    def can_move(self, tile, direction):
        x, y = tile.position
        if direction == "up":
            new_position = (x - 1, y)
        elif direction == "down":
            new_position = (x + 1, y)
        elif direction == "left":
            new_position = (x, y - 1)
        elif direction == "right":
            new_position = (x, y + 1)
        a, b = new_position[0], new_position[1]
        if 0 <= a < TEST_BOARD_SIZE and 0 <= b < TEST_BOARD_SIZE:
            cell = self.board[a][b]
            if cell is None or cell.is_moving:
                return True
        return False

    def update_board(self, old_position, new_position, tile):
        old_x, old_y = old_position
        new_x, new_y = new_position
        self.board[old_x][old_y] = None
        self.board[new_x][new_y] = tile
