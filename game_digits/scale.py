# Модуль для управления масштабом игры
# Измените SCALE для увеличения/уменьшения размеров игрового поля

# Коэффициент масштабирования (1.0 = 100%, 1.10 = 110%)
SCALE = 1.10

# Базовые размеры (без масштабирования)
BASE_TILE_SIZE = 64
BASE_GAP = 3
BASE_TILE_FONT_SIZE = 40


def scaled(value):
    """Масштабирует значение и округляет до целого."""
    return int(value * SCALE)


# Масштабированные размеры для использования в других модулях
TILE_SIZE = scaled(BASE_TILE_SIZE)  # 64 -> 70 при SCALE=1.10
GAP = scaled(BASE_GAP)              # 3 -> 3 при SCALE=1.10
TILE_FONT_SIZE = scaled(BASE_TILE_FONT_SIZE)  # 40 -> 44 при SCALE=1.10
