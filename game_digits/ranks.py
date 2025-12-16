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
# Format: min_score -> list of color stops
# Colors will be muted 35% toward table background for premium look
LEGENDARY_GRADIENTS = {
    3000: [(139, 0, 0), (200, 60, 60)],           # Гроссмейстер: dark red -> muted red
    3100: [(40, 160, 80), (200, 180, 80)],        # Соломон: muted green -> muted gold
    3200: [(40, 180, 200), (60, 110, 200)],       # Сверхчеловек: muted cyan -> blue
    3300: [(200, 100, 40), (200, 60, 70)],        # Титан: muted orange -> muted red
    3400: [(90, 50, 160), (200, 180, 80)],        # Зевс-Демиург: muted violet -> muted gold
    3500: [(30, 20, 60), (50, 40, 100), (80, 60, 140)],  # Unreal: dark indigo base (космос)
}

# Shine animation intervals (ms between shine passes) - rare and elegant
SHINE_INTERVALS = {
    3000: 3500,  # Гроссмейстер: ~3.5s
    3100: 3200,  # Соломон: ~3.2s
    3200: 3000,  # Сверхчеловек: ~3.0s
    3300: 2800,  # Титан: ~2.8s
    3400: 2600,  # Зевс-Демиург: ~2.6s
    3500: 2400,  # Unreal: ~2.4s
}

# Shine duration (how long the shine takes to cross) per rank
SHINE_DURATIONS = {
    3000: 800,   # Гроссмейстер
    3100: 800,   # Соломон
    3200: 900,   # Сверхчеловек
    3300: 900,   # Титан
    3400: 1000,  # Зевс-Демиург
    3500: 1200,  # Unreal: slowest, most elegant
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

    # Draw feathered edge layers (lighter, more subtle) - NO border
    feather_layers = [
        (2, 25),   # outermost: +2px, alpha 25
        (1, 55),   # +1px, alpha 55
    ]

    for expand, alpha in feather_layers:
        layer_rect = (offset_x - expand, offset_y - expand,
                     badge_w + expand * 2, height + expand * 2)
        layer_color = (*bg_color[:3], alpha)
        pygame.draw.rect(temp_surface, layer_color, layer_rect,
                        border_radius=radius + expand)

    # Main badge body
    main_rect = (offset_x, offset_y, badge_w, height)
    main_alpha = 180  # Slightly more transparent for softer look

    if is_legendary and gradient_colors:
        # Create gradient surface
        grad_surface = pygame.Surface((badge_w, height), pygame.SRCALPHA)
        _draw_gradient_rect(grad_surface, (0, 0, badge_w, height), gradient_colors, horizontal=True)

        # Apply capsule mask
        mask_surface = pygame.Surface((badge_w, height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, main_alpha), (0, 0, badge_w, height), border_radius=radius)

        # Combine gradient with mask
        grad_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        temp_surface.blit(grad_surface, (offset_x, offset_y))

        # Add subtle outer glow for Unreal (3500+)
        if rank_score >= 3500:
            glow_rect = (offset_x - 3, offset_y - 3, badge_w + 6, height + 6)
            pygame.draw.rect(temp_surface, (255, 255, 255, 12), glow_rect, border_radius=radius + 3)
    else:
        # Flat color badge
        main_color = (*bg_color[:3], main_alpha)
        pygame.draw.rect(temp_surface, main_color, main_rect, border_radius=radius)

    return temp_surface, is_legendary, (offset_x, offset_y)


def _draw_shine(surface, badge_w, height, offset_x, offset_y, time_ms, rank_score, scale_module):
    """Draw animated shine effect for legendary badges - thin specular highlight."""
    import pygame

    # Get shine interval and duration for this rank tier
    shine_interval = 3500  # default
    shine_duration = 900   # default
    for score in sorted(SHINE_INTERVALS.keys(), reverse=True):
        if rank_score >= score:
            shine_interval = SHINE_INTERVALS[score]
            break
    for score in sorted(SHINE_DURATIONS.keys(), reverse=True):
        if rank_score >= score:
            shine_duration = SHINE_DURATIONS[score]
            break

    # Calculate phase within the cycle
    cycle_time = time_ms % shine_interval
    if cycle_time > shine_duration:
        return  # Not in shine phase

    # Calculate stripe position
    progress = cycle_time / shine_duration
    # Very thin stripe: 12% of badge width
    stripe_w = max(3, int(badge_w * 0.12))
    total_travel = badge_w + stripe_w
    stripe_x = int(progress * total_travel) - stripe_w

    radius = height // 2

    # Create shine surface
    shine_surface = pygame.Surface((badge_w, height), pygame.SRCALPHA)

    # Determine shine color and alpha based on rank
    if rank_score >= 3500:  # Unreal - prismatic/rainbow shine
        alpha_peak = 35  # Brighter for dark background
    elif rank_score == 3300:  # Титан - warm
        alpha_peak = 16
    elif rank_score == 3400:  # Зевс
        alpha_peak = 16
    else:
        alpha_peak = 15  # Very subtle for others

    # Draw thin diagonal shine stripe with soft feathered edges
    for i in range(stripe_w):
        # Strong feather: gaussian-like falloff
        dist_from_center = abs(i - stripe_w // 2) / max(1, stripe_w // 2)
        # Cubic falloff for very soft edges
        falloff = (1 - dist_from_center) ** 3
        alpha = int(alpha_peak * falloff)

        if alpha < 2:
            continue

        # Draw with diagonal skew
        x = stripe_x + i
        if 0 <= x < badge_w:
            for y in range(height):
                skew = int((y - height // 2) * 0.35)  # Slight diagonal
                actual_x = x + skew
                if 0 <= actual_x < badge_w:
                    # Unreal gets prismatic rainbow colors
                    if rank_score >= 3500:
                        # Rainbow based on position
                        hue_shift = (actual_x + y * 0.5) / badge_w
                        if hue_shift < 0.33:
                            shine_color = (100, 200, 255)  # Cyan
                        elif hue_shift < 0.66:
                            shine_color = (200, 100, 255)  # Magenta
                        else:
                            shine_color = (255, 200, 100)  # Gold
                    elif rank_score == 3300:
                        shine_color = (255, 250, 220)  # Warm
                    elif rank_score == 3400:
                        shine_color = (220, 240, 255)  # Cool
                    else:
                        shine_color = (255, 255, 255)  # White
                    shine_surface.set_at((actual_x, y), (*shine_color, alpha))

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
