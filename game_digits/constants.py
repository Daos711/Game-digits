# Размеры сетки (импортируем из scale.py для легкого изменения)
from game_digits import scale

BOARD_SIZE = 10


# Динамические значения - читаются из scale при каждом вызове
def get_tile_size():
    return scale.TILE_SIZE


def get_gap():
    return scale.GAP


# Для обратной совместимости - эти значения обновляются через recalculate()
TILE_SIZE = scale.TILE_SIZE
GAP = scale.GAP

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

# Шаг между диагональными линиями (пиксели)
STRIPE_SPACING = 8


def recalculate():
    """Пересчитать значения после изменения настроек масштаба."""
    global TILE_SIZE, GAP
    TILE_SIZE = scale.TILE_SIZE
    GAP = scale.GAP


def create_background_surface(width, height):
    """Создаёт поверхность с диагональными линиями под углом 60 градусов."""
    import pygame
    import math
    surface = pygame.Surface((width, height))
    surface.fill(BACKGROUND_COLOR)

    # Угол 60 градусов (от горизонтали)
    # tan(60°) = √3 ≈ 1.732
    angle_rad = math.radians(60)
    tan_angle = math.tan(angle_rad)

    # Рисуем диагональные линии из левого нижнего в правый верхний
    # Для угла 60° от горизонтали: dy/dx = tan(60°)
    # Линия идёт снизу-слева вверх-вправо
    spacing = STRIPE_SPACING

    # Нужно покрыть всю поверхность линиями
    # Начинаем с нижнего левого угла и идём вправо и вверх
    max_offset = width + height * tan_angle

    for offset in range(-int(height / tan_angle), int(max_offset), spacing):
        # Точка старта на нижней границе (y = height)
        x1 = offset
        y1 = height
        # Точка конца на верхней границе (y = 0)
        x2 = offset + height / tan_angle
        y2 = 0
        pygame.draw.line(surface, STRIPE_COLOR, (x1, y1), (x2, y2), 1)

    return surface


def grid_to_pixel(row, col):
    """Преобразует координаты сетки в пиксельные координаты (topleft)."""
    tile_size = scale.TILE_SIZE
    gap = scale.GAP
    x = (col + 1) * gap + col * tile_size
    y = (row + 1) * gap + row * tile_size
    return x, y


def grid_to_pixel_center(row, col):
    """Преобразует координаты сетки в пиксельные координаты центра ячейки."""
    x, y = grid_to_pixel(row, col)
    return x + scale.TILE_SIZE // 2, y + scale.TILE_SIZE // 2


def pixel_to_grid(x, y):
    """Преобразует пиксельные координаты в координаты сетки."""
    tile_size = scale.TILE_SIZE
    gap = scale.GAP
    col = (x - gap) // (tile_size + gap)
    row = (y - gap) // (tile_size + gap)
    return row, col


def pixel_to_grid_round(x, y):
    """Преобразует пиксельные координаты в координаты сетки с округлением."""
    tile_size = scale.TILE_SIZE
    gap = scale.GAP
    col = round((x - gap) / (tile_size + gap))
    row = round((y - gap) / (tile_size + gap))
    return row, col
