"""
Rank system based on total score.
Rankings from the original game community.
"""

# Rank definitions: (min_score, name, colors)
# Colors progress from simple to impressive as rank increases
# Each rank has: (primary_color, secondary_color, style)
# style: 'solid', 'gradient', 'gradient_triple', 'rainbow'

RANKS = [
    # Начальные ранги - простые цвета
    (0,    "Новичок",                    ((140, 140, 140), None, 'solid')),
    (1800, "Любитель",                   ((100, 180, 100), None, 'solid')),
    (2000, "Энтузиаст",                  ((80, 160, 80), None, 'solid')),
    (2200, "Юниор",                      ((60, 180, 180), None, 'solid')),

    # Разряды - синяя гамма
    (2300, "3 разряд",                   ((70, 130, 200), None, 'solid')),
    (2400, "2 разряд",                   ((50, 100, 200), None, 'solid')),
    (2500, "1 разряд",                   ((80, 80, 200), (130, 80, 200), 'gradient')),

    # Мастерские ранги - тёплые тона
    (2600, "Кандидат в мастера",         ((180, 80, 180), (220, 100, 150), 'gradient')),
    (2700, "Мастер",                     ((220, 150, 50), (240, 180, 80), 'gradient')),
    (2800, "Мастер международного класса", ((220, 100, 50), (240, 150, 50), 'gradient')),

    # Элитные ранги - красные и золотые
    (2900, "Эксперт",                    ((200, 50, 50), (240, 80, 80), 'gradient')),
    (3000, "Гроссмейстер",               ((180, 30, 60), (220, 50, 80), 'gradient')),
    (3100, "Соломон",                    ((212, 175, 55), (255, 215, 0), 'gradient')),

    # Легендарные ранги - особые эффекты
    (3200, "Сверхчеловек",               ((255, 200, 50), (255, 150, 0), (255, 100, 50), 'gradient_triple')),
    (3300, "Титан",                      ((200, 50, 200), (50, 150, 255), (50, 220, 150), 'gradient_triple')),
    (3400, "Зевс-Демиург",               ((255, 215, 0), (200, 80, 200), (100, 150, 255), 'gradient_triple')),

    # Запредельный ранг - радуга
    (3500, "Unreal",                     ((255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255), 'rainbow')),
]


def get_rank(total_score: int) -> tuple:
    """
    Get rank info for a given total score.

    Returns:
        tuple: (name, colors_info) where colors_info is (color1, color2/None, style)
    """
    rank_name = RANKS[0][1]
    rank_colors = RANKS[0][2]

    for min_score, name, colors in RANKS:
        if total_score >= min_score:
            rank_name = name
            rank_colors = colors
        else:
            break

    return rank_name, rank_colors


def get_rank_name(total_score: int) -> str:
    """Get just the rank name for a given total score."""
    return get_rank(total_score)[0]


def get_rank_index(total_score: int) -> int:
    """Get the rank index (0-based) for a given total score."""
    index = 0
    for i, (min_score, _, _) in enumerate(RANKS):
        if total_score >= min_score:
            index = i
        else:
            break
    return index


def draw_rank_bar(surface, rect, colors_info, time_offset=0):
    """
    Draw a rank color bar on the given surface.

    Args:
        surface: pygame Surface to draw on
        rect: (x, y, width, height) tuple
        colors_info: (color1, color2/more, style) from RANKS
        time_offset: for animated effects (rainbow)
    """
    import pygame

    x, y, width, height = rect

    if colors_info[-1] == 'solid':
        color = colors_info[0]
        pygame.draw.rect(surface, color, rect)

    elif colors_info[-1] == 'gradient':
        color1, color2 = colors_info[0], colors_info[1]
        for i in range(width):
            t = i / max(1, width - 1)
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)
            pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + height - 1))

    elif colors_info[-1] == 'gradient_triple':
        color1, color2, color3 = colors_info[0], colors_info[1], colors_info[2]
        for i in range(width):
            t = i / max(1, width - 1)
            if t < 0.5:
                t2 = t * 2
                r = int(color1[0] + (color2[0] - color1[0]) * t2)
                g = int(color1[1] + (color2[1] - color1[1]) * t2)
                b = int(color1[2] + (color2[2] - color1[2]) * t2)
            else:
                t2 = (t - 0.5) * 2
                r = int(color2[0] + (color3[0] - color2[0]) * t2)
                g = int(color2[1] + (color3[1] - color2[1]) * t2)
                b = int(color2[2] + (color3[2] - color2[2]) * t2)
            pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + height - 1))

    elif colors_info[-1] == 'rainbow':
        # Rainbow gradient with optional animation
        colors = colors_info[:-1]  # All colors except 'rainbow'
        num_colors = len(colors)
        for i in range(width):
            t = ((i / max(1, width - 1)) + time_offset) % 1.0
            segment = t * (num_colors - 1)
            idx1 = int(segment)
            idx2 = min(idx1 + 1, num_colors - 1)
            local_t = segment - idx1

            c1, c2 = colors[idx1], colors[idx2]
            r = int(c1[0] + (c2[0] - c1[0]) * local_t)
            g = int(c1[1] + (c2[1] - c1[1]) * local_t)
            b = int(c1[2] + (c2[2] - c1[2]) * local_t)
            pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + height - 1))

    # Add subtle border
    border_color = (50, 50, 50)
    pygame.draw.rect(surface, border_color, rect, 1)
