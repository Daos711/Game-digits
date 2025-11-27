import random
import pygame

from game_digits.sprites import Tile

TILE_SIZE = 64
GAP = 3
OFFSET = (23, 23)
COLORS = {
    1: (250, 130, 124),
    2: (98, 120, 255),
    3: (249, 204, 122),
    4: (127, 254, 138),
    5: (251, 94, 223),
    6: (126, 253, 205),
    7: (239, 255, 127),
    8: (174, 121, 251),
    9: (255, 152, 123),
}


class Game:
    COUNTDOWN_EVENT = pygame.USEREVENT + 2

    def __init__(self, tiles, time_limit=300):
        self.tiles = tiles
        self.board = [[None for _ in range(10)] for _ in range(10)]
        self.score = 0
        self.time_limit = time_limit
        self.current_time = time_limit
        self.timer_started = False
        self.selected_tile = None
        self.original_color = None
        self.game_over_flag = False
        self.COLORS = COLORS
        self.initialize_tiles()
        self.prepare_to_end = False

    def initialize_tiles(self):
        for i in range(10):
            for j in range(10):
                number = random.randint(1, 9)
                tile = Tile(number, (i, j), COLORS[number])
                self.board[i][j] = tile
                self.tiles.add(tile)

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
        """
        Удаляет пару плиток если они подходят.
        Возвращает None если удаление не удалось,
        или список позиций от первой плитки ко второй для анимации очков.
        """
        if tile1 is None or tile2 is None:
            return None
        if tile1.is_moving or tile2.is_moving:
            return None
        x1, y1 = tile1.position
        x2, y2 = tile2.position
        if tile1.number == tile2.number or tile1.number + tile2.number == 10:
            if x1 == x2:  # Плитки на одной вертикальной линии
                if abs(y1 - y2) == 1 or all(
                    self.board[x1][j] is None for j in range(min(y1, y2) + 1, max(y1, y2))
                ):
                    self.score += (abs(y1 - y2) + 1) * (abs(y1 - y2) + 2) // 2
                    self.board[x1][y1] = None
                    self.board[x2][y2] = None
                    self.tiles.remove(tile1, tile2)
                    self.post_remove_actions()
                    # Возвращаем путь от первой плитки ко второй
                    step = 1 if y2 > y1 else -1
                    positions = [(x1, j) for j in range(y1, y2 + step, step)]
                    return positions
            elif y1 == y2:  # Плитки на одной горизонтальной линии
                if abs(x1 - x2) == 1 or all(
                    self.board[i][y1] is None for i in range(min(x1, x2) + 1, max(x1, x2))
                ):
                    self.score += (abs(x1 - x2) + 1) * (abs(x1 - x2) + 2) // 2
                    self.board[x1][y1] = None
                    self.board[x2][y2] = None
                    self.tiles.remove(tile1, tile2)
                    self.post_remove_actions()
                    # Возвращаем путь от первой плитки ко второй
                    step = 1 if x2 > x1 else -1
                    positions = [(i, y1) for i in range(x1, x2 + step, step)]
                    return positions
        return None

    def add_new_tile(self):
        empty_positions = [
            (i, j) for i in range(10) for j in range(10) if self.board[i][j] is None
        ]
        if empty_positions:
            position = random.choice(empty_positions)
            existing_numbers = set(tile.number for tile in self.tiles)
            possible_numbers = set()
            for num in existing_numbers:
                pair = 10 - num
                possible_numbers.add(num)
                possible_numbers.add(pair)
            if possible_numbers:
                number = random.choice(list(possible_numbers))
                color = self.COLORS[number]
                new_tile = Tile(number, position, color)
                self.tiles.add(new_tile)
                self.board[position[0]][position[1]] = new_tile

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
        if 0 <= a < len(self.board) and 0 <= b < len(self.board[0]):
            cell = self.board[a][b]
            # Клетка свободна или занята движущейся плиткой (которая уходит)
            if cell is None or cell.is_moving:
                return True
        return False

    def update_board(self, old_position, new_position, tile):
        old_x, old_y = old_position
        new_x, new_y = new_position
        self.board[old_x][old_y] = None
        self.board[new_x][new_y] = tile
