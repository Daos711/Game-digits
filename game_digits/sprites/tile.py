import pygame

from game_digits import get_font_path

TILE_SIZE = 64
GAP = 3


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
        self.rect.topleft = (
            (self.y + 1) * GAP + self.y * TILE_SIZE,
            (self.x + 1) * GAP + self.x * TILE_SIZE,
        )
        self.draw_tile((0, 0, 0))

    def draw_tile(self, text_color):
        self.image.fill(self.color)
        pygame.draw.rect(self.image, (71, 74, 72), self.image.get_rect(), 2)
        font = pygame.font.Font(
            get_font_path("OpenSans-VariableFont_wdth,wght.ttf"), 40
        )
        text = font.render(str(self.number), True, text_color)
        text_rect = text.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2))
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

        target_x = (y + 1) * GAP + y * TILE_SIZE
        target_y = (x + 1) * GAP + x * TILE_SIZE
        return pygame.Rect(target_x, target_y, TILE_SIZE, TILE_SIZE)
