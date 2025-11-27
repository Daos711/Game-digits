import random
import pygame
from tile import Tile

tile_size, gap = 64, 3
offset = (23, 23)
COLORS = {1: (250, 130, 124), 2: (98, 120, 255), 3: (249, 204, 122),
          4: (127, 254, 138), 5: (251, 94, 223), 6: (126, 253, 205),
          7: (239, 255, 127), 8: (174, 121, 251), 9: (255, 152, 123)}

class Game:
    COUNTDOWN_EVENT = pygame.USEREVENT + 2
    def __init__(self, tiles, time_limit=300):
        self.tiles = tiles
        self.board = [[None for _ in range(10)] for _ in range(10)]  # Игровое поле
        self.score = 0  # Счет
        self.time_limit = time_limit  # Время игры в секундах
        self.current_time = time_limit  # Текущее оставшееся время
        self.timer_started = False  # Флаг запуска таймера
        self.selected_tile = None
        self.original_color = None
        self.game_over_flag = False  # Флаг окончания игры
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
            self.selected_tile.update_color(self.original_color, (0, 0, 0))  # Восстанавливаем исходный цвет
        self.selected_tile = tile
        self.original_color = tile.color
        tile.update_color((255, 139, 2), (255, 255, 202))  # Меняем цвет плитки и цвет текста

    def deselect_tile(self):
        if self.selected_tile:
            self.selected_tile.update_color(self.original_color, (0, 0, 0))  # Восстанавливаем исходный цвет
            self.selected_tile = None
            self.original_color = None

    def remove_tiles(self, tile1, tile2):
        if tile1 is None or tile2 is None:
            return False
        if tile1.is_moving or tile2.is_moving:
            return False
        x1, y1 = tile1.position
        x2, y2 = tile2.position
        if (tile1.number == tile2.number or tile1.number + tile2.number == 10):  # Проверка условий для удаления плиток
            if x1 == x2:  # Плитки находятся на одной вертикальной линии
                if abs(y1 - y2) == 1 or all(self.board[x1][j] is None for j in range(min(y1, y2) + 1, max(y1, y2))):
                    self.score += (abs(y1 - y2) + 1) * (abs(y1 - y2) + 2) // 2
                    self.board[x1][y1] = None
                    self.board[x2][y2] = None
                    self.tiles.remove(tile1, tile2)  # Удаление плиток из группы спрайтов
                    self.post_remove_actions()
                    return True  # Успешное удаление
            elif y1 == y2:  # Плитки находятся на одной горизонтальной линии
                if abs(x1 - x2) == 1 or all(self.board[i][y1] is None for i in range(min(x1, x2) + 1, max(x1, x2))):
                    self.score += (abs(x1 - x2) + 1) * (abs(x1 - x2) + 2) // 2
                    self.board[x1][y1] = None
                    self.board[x2][y2] = None
                    self.tiles.remove(tile1, tile2)  # Удаление плиток из группы спрайтов
                    self.post_remove_actions()
                    return True  # Успешное удаление
        return False  # Условия для удаления не выполняются

    def add_new_tile(self):
        empty_positions = [(i, j) for i in range(10) for j in range(10) if self.board[i][j] is None]
        if empty_positions:
            position = random.choice(empty_positions)
            # Определяем возможные числа для новой плитки (существующие числа и их пары)
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
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 1000)  # Запуск таймера каждую секунду
            self.timer_started = True

    def stop_timer(self):
        if self.timer_started:
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 0)  # Остановка таймера
            self.timer_started = False

    def handle_countdown(self):
        if self.current_time > 0:
            self.current_time -= 1
            if self.current_time == 0:
                self.game_over_flag = True  # Установить флаг окончания игры
                self.stop_timer()
        else:
            self.game_over_flag = True

    def post_remove_actions(self):
        # Запуск таймера игры после первой успешной удаления пары плиток
        if not self.timer_started:
            self.start_timer()

        # Проверка, остались ли плитки на поле
        if not any(tile for row in self.board for tile in row):
            self.prepare_to_end = True  # Устанавливаем флаг подготовки к завершению игры
            self.stop_timer()

    def deduct_score(self, n):
        deduction = sum(range(1, n + 1))
        self.score = max(0, self.score - deduction)

    def can_move(self, tile, direction):
        x, y = tile.position
        if direction == 'up':
            new_position = (x - 1, y)
        elif direction == 'down':
            new_position = (x + 1, y)
        elif direction == 'left':
            new_position = (x, y - 1)
        elif direction == 'right':
            new_position = (x, y + 1)
        a, b = new_position[0], new_position[1]
        if 0 <= a < len(self.board) and 0 <= b < len(self.board[0]):
            if self.board[a][b] is None:
                return True
        return False

    def update_board(self, old_position, new_position, tile):
        old_x, old_y = old_position
        new_x, new_y = new_position
        self.board[old_x][old_y] = None
        self.board[new_x][new_y] = tile