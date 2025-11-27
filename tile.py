import pygame
from utils import resource_path

tile_size, gap = 64, 3

class Tile(pygame.sprite.Sprite):
    def __init__(self, number, position, color):
        super().__init__()
        self.number = number
        self.position = position
        self.color = color
        self.is_moving = False
        self.current_direction = None
        self.image = pygame.Surface((tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.x = self.position[0]
        self.y = self.position[1]
        self.target_rect = None
        self.rect.topleft = ((self.y + 1) * gap + self.y * tile_size, (self.x + 1) * gap + self.x * tile_size)
        self.draw_tile((0, 0, 0))  # Используем черный цвет для текста при инициализации

    def draw_tile(self, text_color):
        self.image.fill(self.color)
        pygame.draw.rect(self.image, (71, 74, 72), self.image.get_rect(), 2)
        font = pygame.font.Font(resource_path('fonts/OpenSans-VariableFont_wdth,wght.ttf'), 40)
        text = font.render(str(self.number), True, text_color)
        text_rect = text.get_rect(center=(tile_size // 2, tile_size // 2))
        self.image.blit(text, text_rect)

    def update_color(self, new_color, text_color=(255, 255, 202)):
        self.color = new_color
        self.draw_tile(text_color)  # Используем новый цвет для текста при обновлении цвета плитки

    def target_move(self, direction, board):
        x, y = self.position
        if direction == 'up':
            while x > 0 and board[x - 1][y] is None:
                x -= 1
        elif direction == 'down':
            while x < len(board) - 1 and board[x + 1][y] is None:
                x += 1
        elif direction == 'left':
            while y > 0 and board[x][y - 1] is None:
                y -= 1
        elif direction == 'right':
            while y < len(board[0]) - 1 and board[x][y + 1] is None:
                y += 1

        # Вычисляем конечное положение плитки
        target_x = (y + 1) * gap + y * tile_size
        target_y = (x + 1) * gap + x * tile_size
        return pygame.Rect(target_x, target_y, tile_size, tile_size)


