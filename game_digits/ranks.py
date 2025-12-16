"""
Rank system based on total score.
Rankings from the original game community.
"""

# Rank definitions: (min_score, name, fg_color, bg_color)
# fg_color = text color, bg_color = badge background color
RANKS = [
    # Начальные ранги
    (0,    "Новичок",                    (122, 127, 134), (238, 240, 242)),
    (1800, "Любитель",                   (46, 125, 50),   (231, 244, 232)),
    (2000, "Энтузиаст",                  (0, 137, 123),   (224, 245, 242)),
    (2200, "Юниор",                      (30, 136, 229),  (227, 241, 255)),

    # Разряды
    (2300, "3 разряд",                   (166, 106, 46),  (244, 233, 223)),
    (2400, "2 разряд",                   (96, 125, 139),  (233, 238, 242)),
    (2500, "1 разряд",                   (184, 134, 11),  (255, 243, 204)),

    # Мастерские ранги
    (2600, "Кандидат в мастера",         (106, 27, 154),  (241, 230, 250)),
    (2700, "Мастер",                     (40, 53, 147),   (230, 234, 251)),
    (2800, "Мастер международного класса", (0, 102, 204),   (225, 240, 255)),

    # Элитные ранги
    (2900, "Эксперт",                    (13, 71, 161),   (227, 236, 255)),
    (3000, "Гроссмейстер",               (183, 28, 28),   (252, 229, 229)),
    (3100, "Соломон",                    (47, 143, 58),   (230, 255, 233)),

    # Легендарные ранги
    (3200, "Сверхчеловек",               (122, 155, 0),   (243, 255, 224)),
    (3300, "Титан",                      (245, 124, 0),   (255, 233, 214)),
    (3400, "Зевс-Демиург",               (94, 53, 177),   (240, 234, 254)),

    # Запредельный ранг
    (3500, "Unreal",                     (213, 0, 249),   (252, 230, 255)),
]


def get_rank(total_score: int) -> tuple:
    """
    Get rank info for a given total score.

    Returns:
        tuple: (name, fg_color, bg_color)
    """
    rank_name = RANKS[0][1]
    fg_color = RANKS[0][2]
    bg_color = RANKS[0][3]

    for min_score, name, fg, bg in RANKS:
        if total_score >= min_score:
            rank_name = name
            fg_color = fg
            bg_color = bg
        else:
            break

    return rank_name, fg_color, bg_color


def get_rank_name(total_score: int) -> str:
    """Get just the rank name for a given total score."""
    return get_rank(total_score)[0]


def get_rank_index(total_score: int) -> int:
    """Get the rank index (0-based) for a given total score."""
    index = 0
    for i, (min_score, _, _, _) in enumerate(RANKS):
        if total_score >= min_score:
            index = i
        else:
            break
    return index


def draw_rank_badge(surface, rect, rank_name, fg_color, bg_color):
    """
    Draw a rank badge (capsule/pill shape) on the given surface.

    Args:
        surface: pygame Surface to draw on
        rect: (x, y, width, height) tuple
        rank_name: Name of the rank to display
        fg_color: Text color
        bg_color: Background color
    """
    import pygame
    from game_digits import get_font_path, scale

    x, y, width, height = rect

    # Draw pill-shaped background
    radius = height // 2
    pygame.draw.rect(surface, bg_color, rect, border_radius=radius)

    # Draw border (darker than bg for better contrast)
    border_color = tuple(max(0, int(c * 0.75)) for c in bg_color)
    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=radius)

    # Draw text
    font_size = max(10, height - scale.scaled(8))
    font = pygame.font.Font(get_font_path("2204.ttf"), font_size)
    text = font.render(rank_name, True, fg_color)
    text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text, text_rect)


def draw_rank_bar(surface, rect, colors_info, time_offset=0):
    """
    Legacy function for backward compatibility.
    Now draws a simple colored bar.
    """
    import pygame

    x, y, width, height = rect

    # Use first color for solid bar
    if isinstance(colors_info, tuple) and len(colors_info) >= 2:
        # New format: (fg_color, bg_color) - use bg_color for bar
        color = colors_info[1] if len(colors_info) == 2 else colors_info[0]
    else:
        color = colors_info[0] if colors_info else (150, 150, 150)

    pygame.draw.rect(surface, color, rect, border_radius=height // 2)

    # Add subtle border
    border_color = tuple(max(0, int(c * 0.85)) for c in color)
    pygame.draw.rect(surface, border_color, rect, width=1, border_radius=height // 2)
