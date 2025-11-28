import pygame

from game_digits import get_font_path
from game_digits.constants import TILE_SIZE, GAP, TILE_BORDER_COLOR, grid_to_pixel


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
        self.x = self.position[0]
        self.y = self.position[1]
        self.target_rect = None
        x, y = grid_to_pixel(self.x, self.y)
        self.rect.topleft = (x, y)
        self.draw_tile((0, 0, 0))

    def draw_tile(self, text_color):
        self.image.fill(self.color)

        # === НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ ===
        bevel = 4                # Толщина фаски (3-6 оптимально)
        light_factor = 1.25      # Множитель для светлой грани (1.1-1.4)
        dark_factor = 0.65       # Множитель для тёмной грани (0.5-0.8)

        def clamp(x: int) -> int:
            return max(0, min(255, x))

        # Цвета для подсветки и тени
        light = tuple(clamp(int(c * light_factor)) for c in self.color)
        dark = tuple(clamp(int(c * dark_factor)) for c in self.color)

        w, h = self.image.get_size()

        # Верхняя грань (подсветка)
        pygame.draw.rect(self.image, light, (0, 0, w, bevel))
        # Левая грань (подсветка)
        pygame.draw.rect(self.image, light, (0, 0, bevel, h))

        # Нижняя грань (тень)
        pygame.draw.rect(self.image, dark, (0, h - bevel, w, bevel))
        # Правая грань (тень)
        pygame.draw.rect(self.image, dark, (w - bevel, 0, bevel, h))

        # Внутренняя ровная часть (центр тайла)
        pygame.draw.rect(
            self.image,
            self.color,
            (bevel, bevel, w - 2 * bevel, h - 2 * bevel),
        )

        # Тонкая рамка по контуру
        pygame.draw.rect(self.image, TILE_BORDER_COLOR, self.image.get_rect(), 1)

        # Текст
        font = pygame.font.Font(
            get_font_path("OpenSans-VariableFont_wdth,wght.ttf"), 40
        )
        text = font.render(str(self.number), True, text_color)
        text_rect = text.get_rect(center=(w // 2, h // 2))
        self.image.blit(text, text_rect)

    def update_color(self, new_color, text_color=(255, 255, 202)):
        self.color = new_color
        self.draw_tile(text_color)

    def target_move(self, direction, board):
        x, y = self.position
        if direction == "up":
            while x > 0 and board[x - 1][y] is None:
                x -= 1
        elif direction == "down":
            while x < len(board) - 1 and board[x + 1][y] is None:
                x += 1
        elif direction == "left":
            while y > 0 and board[x][y - 1] is None:
                y -= 1
        elif direction == "right":
            while y < len(board[0]) - 1 and board[x][y + 1] is None:
                y += 1

        target_x, target_y = grid_to_pixel(x, y)
        return pygame.Rect(target_x, target_y, TILE_SIZE, TILE_SIZE)
