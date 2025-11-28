# Размеры сетки
TILE_SIZE = 64
GAP = 3
BOARD_SIZE = 10

# Цвета плиток
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

# Цвета интерфейса
BACKGROUND_COLOR = (252, 250, 248)  # Очень светлый, почти белый
STRIPE_COLOR = (240, 238, 235)  # Цвет диагональных линий (чуть темнее фона)
TILE_BORDER_COLOR = (71, 74, 72)

# Размер тайла для фоновой текстуры
BACKGROUND_TILE_SIZE = 8


def create_background_tile():
    """Создаёт тайл 8x8 с диагональной линией для фоновой текстуры."""
    import pygame
    size = BACKGROUND_TILE_SIZE
    tile = pygame.Surface((size, size))
    tile.fill(BACKGROUND_COLOR)
    # Рисуем диагональную линию (из нижнего левого в верхний правый)
    # Линия проходит по диагонали тайла
    for i in range(size):
        tile.set_at((i, size - 1 - i), STRIPE_COLOR)
    return tile


def create_background_surface(width, height):
    """Создаёт поверхность с тайловой текстурой заданного размера."""
    import pygame
    surface = pygame.Surface((width, height))
    tile = create_background_tile()
    tile_size = BACKGROUND_TILE_SIZE
    # Заполняем поверхность тайлами
    for x in range(0, width, tile_size):
        for y in range(0, height, tile_size):
            surface.blit(tile, (x, y))
    return surface


def grid_to_pixel(row, col):
    """Преобразует координаты сетки в пиксельные координаты (topleft)."""
    x = (col + 1) * GAP + col * TILE_SIZE
    y = (row + 1) * GAP + row * TILE_SIZE
    return x, y


def grid_to_pixel_center(row, col):
    """Преобразует координаты сетки в пиксельные координаты центра ячейки."""
    x, y = grid_to_pixel(row, col)
    return x + TILE_SIZE // 2, y + TILE_SIZE // 2


def pixel_to_grid(x, y):
    """Преобразует пиксельные координаты в координаты сетки."""
    col = (x - GAP) // (TILE_SIZE + GAP)
    row = (y - GAP) // (TILE_SIZE + GAP)
    return row, col


def pixel_to_grid_round(x, y):
    """Преобразует пиксельные координаты в координаты сетки с округлением."""
    col = round((x - GAP) / (TILE_SIZE + GAP))
    row = round((y - GAP) / (TILE_SIZE + GAP))
    return row, col
