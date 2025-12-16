import pygame

from game_digits import get_font_path
from game_digits.constants import TILE_SIZE, TILE_BORDER_COLOR, grid_to_pixel
from game_digits.scale import TILE_FONT_SIZE, scaled


class Tile(pygame.sprite.Sprite):
    def __init__(self, number, position, color):
        super().__init__()
        self.number = number
        self.position = position
        self.color = color
        self.is_moving = False
        self.current_direction = None
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.target_rect = None
        self.rect.topleft = grid_to_pixel(self.position[0], self.position[1])
        self.draw_tile((0, 0, 0))

    def draw_tile(self, text_color):
        self.image.fill(self.color)

        # === НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ ===
        bevel = 3  # Толщина фаски (не масштабируется для сохранения объёма)
        dark_factor = 0.4        # Множитель для тёмной грани (0.5-0.8)

        def clamp(x: int) -> int:
            return max(0, min(255, x))

        # Цвет для тени
        dark = tuple(clamp(int(c * dark_factor)) for c in self.color)

        w, h = self.image.get_size()

        # Нижняя грань (тень)
        pygame.draw.rect(self.image, dark, (0, h - bevel, w, bevel))
        # Правая грань (тень)
        pygame.draw.rect(self.image, dark, (w - bevel, 0, bevel, h))

        # Тонкая рамка по контуру
        pygame.draw.rect(self.image, TILE_BORDER_COLOR, self.image.get_rect(), 1)

        # Текст
        font = pygame.font.Font(
            get_font_path("OpenSans-VariableFont_wdth,wght.ttf"), TILE_FONT_SIZE
        )
        text = font.render(str(self.number), True, text_color)
        text_rect = text.get_rect(center=(w // 2, h // 2))
        self.image.blit(text, text_rect)

    def update_color(self, new_color, text_color=(255, 255, 202)):
        self.color = new_color
        self.draw_tile(text_color)

    def target_move(self, direction, board):
        x, y = self.position

        def cell_is_passable(cell):
            # Ячейка проходима если пуста или занята движущейся плиткой (она уезжает)
            return cell is None or cell.is_moving

        if direction == "up":
            while x > 0 and cell_is_passable(board[x - 1][y]):
                x -= 1
        elif direction == "down":
            while x < len(board) - 1 and cell_is_passable(board[x + 1][y]):
                x += 1
        elif direction == "left":
            while y > 0 and cell_is_passable(board[x][y - 1]):
                y -= 1
        elif direction == "right":
            while y < len(board[0]) - 1 and cell_is_passable(board[x][y + 1]):
                y += 1

        target_x, target_y = grid_to_pixel(x, y)
        return pygame.Rect(target_x, target_y, TILE_SIZE, TILE_SIZE)
