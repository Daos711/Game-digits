"""
Rank system based on total score.
Rankings from the original game community.
"""
import math

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
    (2800, "Мастер международного класса", (255, 255, 255), (100, 149, 237)),

    # Элитные ранги
    (2900, "Эксперт",                    (255, 255, 255), (70, 100, 180)),

    # Легендарные ранги (3000+) - gradient backgrounds
    (3000, "Гроссмейстер",               (255, 255, 255), (183, 28, 28)),
    (3100, "Соломон",                    (255, 255, 255), (0, 200, 83)),
    (3200, "Сверхчеловек",               (255, 255, 255), (0, 229, 255)),
    (3300, "Титан",                      (255, 255, 255), (255, 109, 0)),
    (3400, "Зевс-Демиург",               (255, 255, 255), (94, 53, 177)),
    (3500, "Unreal",                     (255, 255, 255), (0, 229, 255)),
]

# Gradient definitions for legendary ranks (3000+)
# Format: min_score -> list of color stops [(color, position), ...]
LEGENDARY_GRADIENTS = {
    3000: [(139, 0, 0), (229, 57, 53)],           # Гроссмейстер: dark red -> red
    3100: [(0, 200, 83), (255, 213, 79)],         # Соломон: green -> gold
    3200: [(0, 229, 255), (124, 77, 255)],        # Сверхчеловек: cyan -> purple
    3300: [(255, 109, 0), (255, 23, 68)],         # Титан: orange -> red
    3400: [(94, 53, 177), (0, 229, 255)],         # Зевс-Демиург: purple -> cyan
    3500: [(0, 229, 255), (213, 0, 249), (255, 214, 0)],  # Unreal: cyan -> magenta -> gold
}

# Shine animation intervals (ms between shine passes)
SHINE_INTERVALS = {
    3000: 2800,  # Гроссмейстер
    3100: 2800,  # Соломон
    3200: 2000,  # Сверхчеловек
    3300: 2000,  # Титан
    3400: 1400,  # Зевс-Демиург
    3500: 1400,  # Unreal
}

# Badge surface cache: (rank_name, badge_w, badge_h) -> (static_surface, is_legendary)
_badge_cache = {}


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


def get_rank_score(rank_name: str) -> int:
    """Get the minimum score for a rank by name."""
    for min_score, name, _, _ in RANKS:
        if name == rank_name:
            return min_score
    return 0


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _draw_gradient_rect(surface, rect, colors, horizontal=True):
    """Draw a gradient rectangle with multiple color stops."""
    import pygame

    x, y, w, h = rect
    n_colors = len(colors)

    if n_colors < 2:
        pygame.draw.rect(surface, colors[0] if colors else (128, 128, 128), rect)
        return

    if horizontal:
        for i in range(w):
            t = i / max(1, w - 1)
            # Find which segment we're in
            segment = min(int(t * (n_colors - 1)), n_colors - 2)
            local_t = (t * (n_colors - 1)) - segment
            color = _lerp_color(colors[segment], colors[segment + 1], local_t)
            pygame.draw.line(surface, color, (x + i, y), (x + i, y + h - 1))
    else:
        for i in range(h):
            t = i / max(1, h - 1)
            segment = min(int(t * (n_colors - 1)), n_colors - 2)
            local_t = (t * (n_colors - 1)) - segment
            color = _lerp_color(colors[segment], colors[segment + 1], local_t)
            pygame.draw.line(surface, color, (x, y + i), (x + w - 1, y + i))


def _create_badge_surface(badge_w, height, bg_color, rank_score, scale_module):
    """Create the static badge surface (cached)."""
    import pygame

    radius = height // 2
    expand_max = 4
    temp_w = badge_w + expand_max * 2 + scale_module.scaled(4)
    temp_h = height + expand_max * 2 + scale_module.scaled(4)
    offset_x = expand_max + scale_module.scaled(2)
    offset_y = expand_max + scale_module.scaled(1)

    temp_surface = pygame.Surface((temp_w, temp_h), pygame.SRCALPHA)

    # Draw subtle shadow (offset down-right)
    shadow_rect = (offset_x + 1, offset_y + 2, badge_w, height)
    pygame.draw.rect(temp_surface, (0, 0, 0, 18), shadow_rect, border_radius=radius)

    # Check if legendary (3000+)
    is_legendary = rank_score >= 3000
    gradient_colors = None

    if is_legendary:
        # Find gradient for this rank
        for score in sorted(LEGENDARY_GRADIENTS.keys(), reverse=True):
            if rank_score >= score:
                gradient_colors = LEGENDARY_GRADIENTS[score]
                break

    # Draw feathered edge layers (from outside to inside) - NO border, just alpha layers
    feather_layers = [
        (4, 32),   # outermost: +4px, alpha 32
        (2, 65),   # +2px, alpha 65
        (1, 105),  # +1px, alpha 105
    ]

    for expand, alpha in feather_layers:
        layer_rect = (offset_x - expand, offset_y - expand,
                     badge_w + expand * 2, height + expand * 2)
        layer_color = (*bg_color[:3], alpha)
        pygame.draw.rect(temp_surface, layer_color, layer_rect,
                        border_radius=radius + expand)

    # Main badge body
    main_rect = (offset_x, offset_y, badge_w, height)

    if is_legendary and gradient_colors:
        # Create gradient surface
        grad_surface = pygame.Surface((badge_w, height), pygame.SRCALPHA)
        _draw_gradient_rect(grad_surface, (0, 0, badge_w, height), gradient_colors, horizontal=True)

        # Apply capsule mask
        mask_surface = pygame.Surface((badge_w, height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, 195), (0, 0, badge_w, height), border_radius=radius)

        # Combine gradient with mask
        grad_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        temp_surface.blit(grad_surface, (offset_x, offset_y))
    else:
        # Flat color badge
        main_color = (*bg_color[:3], 195)
        pygame.draw.rect(temp_surface, main_color, main_rect, border_radius=radius)

    return temp_surface, is_legendary, (offset_x, offset_y)


def _draw_shine(surface, badge_w, height, offset_x, offset_y, time_ms, rank_score, scale_module):
    """Draw animated shine effect for legendary badges."""
    import pygame

    # Get shine interval for this rank tier
    shine_interval = 2500  # default
    for score in sorted(SHINE_INTERVALS.keys(), reverse=True):
        if rank_score >= score:
            shine_interval = SHINE_INTERVALS[score]
            break

    # Shine pass duration (how long the stripe takes to cross)
    shine_duration = 600  # ms

    # Calculate phase within the cycle
    cycle_time = time_ms % shine_interval
    if cycle_time > shine_duration:
        return  # Not in shine phase

    # Calculate stripe position
    progress = cycle_time / shine_duration
    stripe_w = int(badge_w * 0.35)
    total_travel = badge_w + stripe_w
    stripe_x = int(progress * total_travel) - stripe_w

    radius = height // 2

    # Create shine surface
    shine_surface = pygame.Surface((badge_w, height), pygame.SRCALPHA)

    # Draw diagonal shine stripe with feathered edges
    for i in range(stripe_w):
        # Feather: alpha peaks in center, fades at edges
        dist_from_center = abs(i - stripe_w // 2) / (stripe_w // 2)
        alpha = int(50 * (1 - dist_from_center * dist_from_center))  # Quadratic falloff

        # Draw vertical line (we'll skew it for diagonal effect)
        x = stripe_x + i
        if 0 <= x < badge_w:
            # Diagonal offset based on y position
            for y in range(height):
                skew = int((y - height // 2) * 0.4)  # -25 degree angle approx
                actual_x = x + skew
                if 0 <= actual_x < badge_w:
                    # Get current pixel and add shine
                    shine_surface.set_at((actual_x, y), (255, 255, 255, alpha))

    # Apply capsule mask to shine
    mask_surface = pygame.Surface((badge_w, height), pygame.SRCALPHA)
    pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, badge_w, height), border_radius=radius)
    shine_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Blit shine to main surface
    surface.blit(shine_surface, (offset_x, offset_y), special_flags=pygame.BLEND_RGBA_ADD)


def draw_rank_badge(surface, rect, rank_name, fg_color, bg_color, max_width=None, time_ms=0):
    """
    Draw a rank badge (capsule/pill shape) with auto-sizing and soft edges.
    For legendary ranks (3000+), draws gradient background with animated shine.

    Args:
        surface: pygame Surface to draw on
        rect: (x, y, width, height) tuple - x,y is center position, width is max width, height is badge height
        rank_name: Name of the rank to display
        fg_color: Text color
        bg_color: Background color
        max_width: Maximum allowed width (optional, uses rect width if not set)
        time_ms: Current time in milliseconds (for animation)
    """
    import pygame
    from game_digits import get_font_path, scale

    center_x, center_y, given_width, height = rect
    max_w = max_width if max_width else given_width
    pad_x = scale.scaled(18)  # Horizontal padding around text
    min_font_size = scale.scaled(12)
    base_font_size = max(min_font_size, height - scale.scaled(4))

    # Find the right font size that fits
    font_size = base_font_size
    font = pygame.font.Font(get_font_path("2204.ttf"), font_size)
    text_surf = font.render(rank_name, True, fg_color)
    text_w = text_surf.get_width()
    badge_w = text_w + 2 * pad_x

    # Reduce font size if needed to fit
    while badge_w > max_w and font_size > min_font_size:
        font_size -= 2  # Step by 2 for faster convergence
        font = pygame.font.Font(get_font_path("2204.ttf"), font_size)
        text_surf = font.render(rank_name, True, fg_color)
        text_w = text_surf.get_width()
        badge_w = text_w + 2 * pad_x

    # Final clamp
    badge_w = min(badge_w, max_w)

    # Get rank score for legendary detection
    rank_score = get_rank_score(rank_name)

    # Cache key
    cache_key = (rank_name, badge_w, height, bg_color[:3])

    # Get or create cached badge surface
    if cache_key not in _badge_cache:
        badge_surface, is_legendary, offsets = _create_badge_surface(
            badge_w, height, bg_color, rank_score, scale
        )
        _badge_cache[cache_key] = (badge_surface.copy(), is_legendary, offsets)

    cached_surface, is_legendary, (offset_x, offset_y) = _badge_cache[cache_key]

    # Calculate badge position (centered at center_x, center_y)
    badge_x = center_x - badge_w // 2
    badge_y = center_y - height // 2

    # Create working copy for this frame
    working_surface = cached_surface.copy()

    # Add animated shine for legendary ranks
    if is_legendary and time_ms > 0:
        _draw_shine(working_surface, badge_w, height, offset_x, offset_y, time_ms, rank_score, scale)

    # Blit badge to main surface
    surface.blit(working_surface, (badge_x - offset_x, badge_y - offset_y))

    # Draw text on main surface (crisp, on top)
    text_rect = text_surf.get_rect(center=(center_x, center_y))
    surface.blit(text_surf, text_rect)


def draw_rank_bar(surface, rect, colors_info, time_offset=0):
    """
    Legacy function for backward compatibility.
    Now draws a simple colored bar.
    """
    import pygame

    x, y, width, height = rect

    # Use first color for solid bar
    if isinstance(colors_info, tuple) and len(colors_info) >= 2:
        color = colors_info[1] if len(colors_info) == 2 else colors_info[0]
    else:
        color = colors_info[0] if colors_info else (150, 150, 150)

    pygame.draw.rect(surface, color, rect, border_radius=height // 2)


def clear_badge_cache():
    """Clear the badge surface cache (call when resolution changes)."""
    global _badge_cache
    _badge_cache = {}
