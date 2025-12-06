"""UI components for the right panel."""
import pygame
import pygame.gfxdraw
import math

from game_digits.scale import scaled, CORNER_RADIUS, BORDER_WIDTH


def draw_rounded_rect(surface, color, rect, radius):
    """Draw a rounded rectangle."""
    x, y, w, h = rect
    radius = min(radius, h // 2, w // 2)

    # Draw the main rectangle parts
    pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))

    # Draw the four corners
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)


def draw_gradient_rounded_rect(surface, rect, color_top, color_bottom, radius):
    """Draw a rounded rectangle with vertical gradient."""
    x, y, w, h = rect

    # Create a temporary surface for the gradient
    temp_surface = pygame.Surface((w, h), pygame.SRCALPHA)

    # Draw gradient line by line
    for i in range(h):
        t = i / h
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(temp_surface, (r, g, b), (0, i), (w, i))

    # Create mask for rounded corners
    mask_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_rounded_rect(mask_surface, (255, 255, 255, 255), (0, 0, w, h), radius)

    # Apply mask
    temp_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    surface.blit(temp_surface, (x, y))


def draw_pause_button(surface, rect, font, text="пауза", is_pressed=False):
    """Draw the pause button with gradient - like reference."""
    x, y, w, h = rect
    radius = scaled(8)  # Менее скруглённые углы

    if is_pressed:
        # Более тёмные цвета при нажатии
        color_top = (200, 135, 0)       # Тёмнее оригинала
        color_bottom = (150, 100, 0)    # Тёмнее оригинала
    else:
        # Градиент: верх RGB(243, 165, 0), низ RGB(186, 127, 0)
        color_top = (243, 165, 0)
        color_bottom = (186, 127, 0)

    # Рисуем кнопку с градиентом
    draw_gradient_rounded_rect(surface, rect, color_top, color_bottom, radius)

    # Белый жирный текст строго по центру с небольшой тенью
    text_surface = font.render(text, True, (255, 255, 255))
    shadow_text = font.render(text, True, (140, 95, 0))

    # Вычисляем центр кнопки
    center_x = x + w // 2
    center_y = y + h // 2

    # Позиционируем текст строго по центру (с небольшим сдвигом вверх для визуального баланса)
    text_x = center_x - text_surface.get_width() // 2
    text_y = center_y - text_surface.get_height() // 2 - 2

    # Тень (смещение на 1 пиксель)
    surface.blit(shadow_text, (text_x + 1, text_y + 1))
    # Основной текст
    surface.blit(text_surface, (text_x, text_y))

    return pygame.Rect(x, y, w, h)


def draw_clock_icon(surface, center, size):
    """Draw clock icon - yellow circle with clock hands (like reference)."""
    x, y = center
    radius = size // 2

    # Жёлто-оранжевый градиент для круга
    # Светло-жёлтый внешний
    pygame.draw.circle(surface, (255, 210, 70), (x, y), radius)
    # Более светлый центр для объёма
    pygame.draw.circle(surface, (255, 230, 100), (x, y), int(radius * 0.7))
    # Тёмно-оранжевый контур
    pygame.draw.circle(surface, (200, 150, 40), (x, y), radius, BORDER_WIDTH)

    # Стрелки часов (тёмно-коричневые)
    hand_color = (80, 50, 20)

    # Часовая стрелка (короткая, указывает на ~10)
    hour_length = radius * 0.45
    hour_angle = math.radians(-120)  # 10 часов
    hour_end_x = x + hour_length * math.cos(hour_angle)
    hour_end_y = y + hour_length * math.sin(hour_angle)
    pygame.draw.line(surface, hand_color, (x, y), (hour_end_x, hour_end_y), max(1, scaled(3)))

    # Минутная стрелка (длинная, указывает на ~2)
    min_length = radius * 0.65
    min_angle = math.radians(-30)  # 2 часа
    min_end_x = x + min_length * math.cos(min_angle)
    min_end_y = y + min_length * math.sin(min_angle)
    pygame.draw.line(surface, hand_color, (x, y), (min_end_x, min_end_y), BORDER_WIDTH)

    # Центральная точка
    pygame.draw.circle(surface, hand_color, (x, y), max(1, scaled(3)))


def draw_sun_icon(surface, center, size):
    """Draw sun icon - yellow/orange circle with triangular rays."""
    x, y = center
    radius = size // 3
    ray_length = size // 2

    # Цвета для солнца (оранжево-жёлтые)
    ray_color = (255, 180, 40)
    sun_outer = (255, 190, 50)
    sun_inner = (255, 220, 100)

    # Рисуем лучи как треугольники
    num_rays = 8
    ray_width = radius * 0.5  # Ширина основания луча

    for i in range(num_rays):
        angle = math.radians(i * 360 / num_rays - 90)
        # Вершина луча
        tip_x = x + ray_length * math.cos(angle)
        tip_y = y + ray_length * math.sin(angle)
        # Два угла основания луча
        base_angle1 = angle + math.radians(15)
        base_angle2 = angle - math.radians(15)
        base1_x = x + radius * math.cos(base_angle1)
        base1_y = y + radius * math.sin(base_angle1)
        base2_x = x + radius * math.cos(base_angle2)
        base2_y = y + radius * math.sin(base_angle2)

        pygame.draw.polygon(surface, ray_color, [
            (tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)
        ])

    # Центральный круг (с градиентом)
    pygame.draw.circle(surface, sun_outer, (x, y), radius)
    pygame.draw.circle(surface, sun_inner, (x, y), int(radius * 0.6))
    # Тёмный контур
    pygame.draw.circle(surface, (200, 140, 30), (x, y), radius, BORDER_WIDTH)


def draw_value_bar(surface, rect, value, font):
    """Draw the blue value bar with number inside - like reference."""
    x, y, w, h = rect
    radius = scaled(4)  # Более угловатые края

    # Голубой градиент сверху вниз (из оригинала)
    color_top = (44, 133, 183)
    color_bottom = (89, 184, 237)

    # Рисуем основную полоску
    draw_gradient_rounded_rect(surface, rect, color_top, color_bottom, radius)

    # Белое число по центру с небольшой тенью
    # Тень
    shadow_surface = font.render(str(value), True, (40, 80, 120))
    shadow_rect = shadow_surface.get_rect(center=(x + w // 2 + 1, y + h // 2 + 1))
    surface.blit(shadow_surface, shadow_rect)
    # Основной текст
    text_surface = font.render(str(value), True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
    surface.blit(text_surface, text_rect)


def draw_progress_bar(surface, rect, progress, radius=None):
    """Draw progress bar with blue background and two-color yellow fill."""
    x, y, w, h = rect
    if radius is None:
        radius = scaled(4)  # Более угловатые края как у value bar

    # 1. Сначала рисуем синий фон (как у value bar)
    bg_color_top = (44, 133, 183)
    bg_color_bottom = (89, 184, 237)
    draw_gradient_rounded_rect(surface, rect, bg_color_top, bg_color_bottom, radius)

    # 2. Затем рисуем жёлтую заполненную часть поверх
    # Верхние 2/3 высоты - RGB(255, 192, 41), нижняя 1/3 - RGB(211, 136, 0)
    bar_width = int(w * progress)
    if bar_width > 0:  # Рисуем при любом положительном прогрессе
        # Адаптивный радиус скругления - уменьшается пропорционально ширине
        actual_radius = min(radius, bar_width // 2)

        # Создаём временную поверхность с градиентом
        temp_surface = pygame.Surface((bar_width, h), pygame.SRCALPHA)

        # Градиент сверху вниз
        top_color = (255, 192, 41)
        bottom_color = (211, 136, 0)
        for row in range(h):
            t = row / max(h - 1, 1)  # 0.0 сверху, 1.0 снизу
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
            pygame.draw.line(temp_surface, (r, g, b), (0, row), (bar_width, row))

        # Создаём маску для скруглённых углов (с адаптивным радиусом)
        mask_surface = pygame.Surface((bar_width, h), pygame.SRCALPHA)
        if actual_radius > 0:
            draw_rounded_rect(mask_surface, (255, 255, 255, 255), (0, 0, bar_width, h), actual_radius)
        else:
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, bar_width, h))

        # Применяем маску
        temp_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(temp_surface, (x, y))


def draw_close_button(surface, rect, is_pressed=False):
    """Draw a square glossy close button with X.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the button
        is_pressed: If True, draw pressed state

    Returns:
        pygame.Rect of the button
    """
    x, y, w, h = rect
    radius = scaled(8)  # Сильно скруглённые углы для квадратной кнопки

    # Colors - RGB(208, 152, 6) base
    if is_pressed:
        color_top = (180, 132, 6)       # Darker when pressed
        color_bottom = (140, 100, 4)
        y_offset = 1
    else:
        color_top = (230, 175, 30)      # Lighter top for gloss
        color_bottom = (176, 126, 2)    # Darker bottom
        y_offset = 0

    # Create temp surface for the button
    btn_surface = pygame.Surface((w, h), pygame.SRCALPHA)

    # Draw glossy gradient
    for row in range(h):
        progress = row / h
        # Upper half lighter, lower half darker
        if progress < 0.5:
            t = progress * 2
            r = int(color_top[0] + (208 - color_top[0]) * t)
            g = int(color_top[1] + (152 - color_top[1]) * t)
            b = int(color_top[2] + (6 - color_top[2]) * t)
        else:
            t = (progress - 0.5) * 2
            r = int(208 + (color_bottom[0] - 208) * t)
            g = int(152 + (color_bottom[1] - 152) * t)
            b = int(6 + (color_bottom[2] - 6) * t)
        pygame.draw.line(btn_surface, (r, g, b), (0, row), (w, row))

    # Apply rounded corner mask
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_rounded_rect(mask, (255, 255, 255, 255), (0, 0, w, h), radius)
    btn_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Blit button
    surface.blit(btn_surface, (x, y + y_offset))

    # Draw light border
    border_color = (255, 220, 120)
    # Top border (lighter)
    pygame.draw.line(surface, border_color, (x + radius, y + y_offset), (x + w - radius, y + y_offset), 1)

    # Draw X - RGB(243, 241, 153) light cream-yellow
    x_color = (243, 241, 153)
    center_x = x + w // 2
    center_y = y + h // 2 + y_offset
    x_size = min(w, h) // 4  # Size of X arms

    # Thick X lines
    line_width = max(1, scaled(4))
    pygame.draw.line(surface, x_color, (center_x - x_size, center_y - x_size),
                    (center_x + x_size, center_y + x_size), line_width)
    pygame.draw.line(surface, x_color, (center_x - x_size, center_y + x_size),
                    (center_x + x_size, center_y - x_size), line_width)

    return pygame.Rect(x, y, w, h)


def draw_result_window_header(surface, rect, title, font, close_pressed=False):
    """Draw the yellow header bar with title and close button.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the header
        title: Title text to display
        font: Font for the title
        close_pressed: If True, draw close button in pressed state

    Returns:
        pygame.Rect of the close button
    """
    x, y, w, h = rect
    radius = CORNER_RADIUS

    # Header background - yellow RGB(254, 211, 113)
    header_color = (254, 211, 113)

    # Draw rounded top corners only
    # Top-left corner
    pygame.draw.circle(surface, header_color, (x + radius, y + radius), radius)
    # Top-right corner
    pygame.draw.circle(surface, header_color, (x + w - radius, y + radius), radius)
    # Fill the rest of the header
    pygame.draw.rect(surface, header_color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surface, header_color, (x, y + radius, w, h - radius))

    # Title text - RGB(4, 72, 111), centered
    title_color = (4, 72, 111)
    title_surface = font.render(title, True, title_color)
    title_rect = title_surface.get_rect(center=(x + w // 2, y + h // 2))
    surface.blit(title_surface, title_rect)

    # Close button - square with rounded corners
    btn_size = scaled(32)
    btn_margin = scaled(8)
    btn_x = x + w - btn_size - btn_margin
    btn_y = y + (h - btn_size) // 2

    close_rect = draw_close_button(surface, (btn_x, btn_y, btn_size, btn_size), is_pressed=close_pressed)

    return close_rect


def draw_rounded_rect_alpha(surface, color, rect, radius, alpha=180):
    """Draw a rounded rectangle with alpha transparency."""
    x, y, w, h = rect
    radius = min(radius, h // 2, w // 2)

    # Create a temporary surface and draw opaque rounded rect
    temp = pygame.Surface((w, h), pygame.SRCALPHA)

    # Draw opaque rounded rectangle using the standard function
    draw_rounded_rect(temp, (*color, 255), (0, 0, w, h), radius)

    # Apply alpha to the entire surface
    temp.set_alpha(alpha)

    surface.blit(temp, (x, y))


def draw_result_row(surface, rect, label, value, label_font, value_font):
    """Draw a result row with semi-transparent blue background.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the row
        label: Text label (e.g., "Ваш результат:")
        value: Numeric value to display
        label_font: Font for the label
        value_font: Font for the value (larger)
    """
    x, y, w, h = rect
    radius = scaled(10)
    border_width = BORDER_WIDTH

    # Create temp surface for proper alpha handling
    temp = pygame.Surface((w, h), pygame.SRCALPHA)

    # Draw border first (filled rounded rect)
    border_color = (120, 170, 190)  # Darker border for visibility
    draw_rounded_rect(temp, (*border_color, 255), (0, 0, w, h), radius)

    # Draw background on top (smaller by border_width)
    bg_color = (168, 212, 242)
    inner_radius = max(1, radius - border_width)
    draw_rounded_rect(temp, (*bg_color, 255),
                      (border_width, border_width, w - 2 * border_width, h - 2 * border_width),
                      inner_radius)

    # Apply transparency
    temp.set_alpha(170)
    surface.blit(temp, (x, y))

    # Text color - RGB(40, 92, 120)
    text_color = (40, 92, 120)

    # Label on the left
    text_padding = scaled(15)
    label_surface = label_font.render(label, True, text_color)
    label_rect = label_surface.get_rect(midleft=(x + text_padding, y + h // 2))
    surface.blit(label_surface, label_rect)

    # Value on the right (larger font)
    value_surface = value_font.render(str(value), True, text_color)
    value_rect = value_surface.get_rect(midright=(x + w - text_padding, y + h // 2))
    surface.blit(value_surface, value_rect)


def draw_congratulation_panel(surface, rect, text, font):
    """Draw the congratulation panel with cream background.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the panel
        text: Text to display (e.g., "Поздравляем!")
        font: Font for the text
    """
    x, y, w, h = rect
    radius = scaled(6)

    # Background - RGB(255, 238, 196)
    bg_color = (255, 238, 196)
    draw_rounded_rect(surface, bg_color, rect, radius)

    # Text color - RGB(166, 63, 42)
    text_color = (166, 63, 42)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
    surface.blit(text_surface, text_rect)


def draw_new_game_button(surface, rect, font, is_pressed=False, text="Новая игра"):
    """Draw glossy yellow-orange button.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the button
        font: Font for the button text
        is_pressed: If True, draw pressed state
        text: Button text (default: "Новая игра")

    Returns:
        pygame.Rect of the button
    """
    x, y, w, h = rect
    radius = scaled(20)  # Сильно скруглённые углы

    # Colors
    if is_pressed:
        color_top = (220, 183, 97)      # Darker when pressed
        color_bottom = (146, 106, 2)
        border_color = (180, 130, 40)
        y_offset = 2  # Shift down when pressed
    else:
        color_top = (250, 213, 117)     # RGB(250, 213, 117) - светлая верхняя часть
        color_bottom = (176, 126, 2)    # RGB(176, 126, 2) - тёмная нижняя часть
        border_color = (255, 230, 150)  # Светлая кайма
        y_offset = 0

    # Create temp surface for the button
    btn_surface = pygame.Surface((w, h), pygame.SRCALPHA)

    # Draw glossy effect with curved boundary
    for row in range(h):
        # Create curved boundary - the dividing line is an arc
        # Peak is at center, edges are lower
        center_x = w // 2
        curve_factor = 0.3  # How pronounced the curve is
        # For each column, calculate where the boundary would be
        progress = row / h

        # Upper portion is lighter, lower is darker
        # The boundary follows a smooth curve
        boundary_progress = 0.4 + curve_factor * math.sin(math.pi * 0.5)

        if progress < boundary_progress:
            # Upper part - interpolate from top to mid
            t = progress / boundary_progress
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t * 0.3)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t * 0.3)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t * 0.3)
        else:
            # Lower part - interpolate from mid to bottom
            t = (progress - boundary_progress) / (1 - boundary_progress)
            mid_r = int(color_top[0] + (color_bottom[0] - color_top[0]) * 0.3)
            mid_g = int(color_top[1] + (color_bottom[1] - color_top[1]) * 0.3)
            mid_b = int(color_top[2] + (color_bottom[2] - color_top[2]) * 0.3)
            r = int(mid_r + (color_bottom[0] - mid_r) * t)
            g = int(mid_g + (color_bottom[1] - mid_g) * t)
            b = int(mid_b + (color_bottom[2] - mid_b) * t)

        pygame.draw.line(btn_surface, (r, g, b), (0, row), (w, row))

    # Apply rounded corner mask
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_rounded_rect(mask, (255, 255, 255, 255), (0, 0, w, h), radius)
    btn_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Draw border
    # Draw rounded rect outline by drawing two rects
    border_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_rounded_rect(border_surface, (*border_color, 255), (0, 0, w, h), radius)
    draw_rounded_rect(border_surface, (0, 0, 0, 0), (2, 2, w - 4, h - 4), radius - 2)

    # Blit button to surface
    surface.blit(btn_surface, (x, y + y_offset))

    # Draw light border outline
    # Top and left edges lighter
    for i in range(2):
        pygame.draw.arc(surface, border_color, (x + i, y + y_offset + i, radius * 2, radius * 2),
                       math.pi / 2, math.pi, 1)
        pygame.draw.arc(surface, border_color, (x + w - radius * 2 - i, y + y_offset + i, radius * 2, radius * 2),
                       0, math.pi / 2, 1)
        pygame.draw.line(surface, border_color, (x + radius, y + y_offset + i), (x + w - radius, y + y_offset + i), 1)

    # Text - dark blue for contrast on yellow-orange button
    text_surface = font.render(text, True, (20, 60, 120))

    # Shadow - light yellow for depth effect
    shadow_surface = font.render(text, True, (255, 230, 150))
    shadow_rect = shadow_surface.get_rect(center=(x + w // 2 + 1, y + h // 2 + y_offset))
    surface.blit(shadow_surface, shadow_rect)

    # Main text (визуально по центру)
    text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2 - 1 + y_offset))
    surface.blit(text_surface, text_rect)

    return pygame.Rect(x, y, w, h)


def draw_checkered_background(surface, rect, cell_size=18):
    """Draw a checkered (grid) background like a school notebook.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the area
        cell_size: Size of each grid cell
    """
    x, y, w, h = rect

    # Fill with white
    pygame.draw.rect(surface, (255, 255, 255), rect)

    # Draw grid lines - RGB(218, 236, 241) light blue
    line_color = (218, 236, 241)

    # Vertical lines
    for lx in range(x, x + w + 1, cell_size):
        pygame.draw.line(surface, line_color, (lx, y), (lx, y + h), 1)

    # Horizontal lines
    for ly in range(y, y + h + 1, cell_size):
        pygame.draw.line(surface, line_color, (x, ly), (x + w, ly), 1)


def draw_checkered_background_rounded(surface, rect, cell_size=18, top_radius=12, bottom_radius=12):
    """Draw a checkered (grid) background with rounded corners.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the area
        cell_size: Size of each grid cell
        top_radius: Radius for top corners (0 for square)
        bottom_radius: Radius for bottom corners (0 for square)
    """
    x, y, w, h = rect

    # Create temp surface for the checkered pattern
    temp_surface = pygame.Surface((w, h), pygame.SRCALPHA)

    # Fill with white
    temp_surface.fill((255, 255, 255, 255))

    # Draw grid lines - deeper blue for better visibility
    line_color = (170, 210, 230, 255)

    # Vertical lines
    for lx in range(0, w + 1, cell_size):
        pygame.draw.line(temp_surface, line_color, (lx, 0), (lx, h), 1)

    # Horizontal lines
    for ly in range(0, h + 1, cell_size):
        pygame.draw.line(temp_surface, line_color, (0, ly), (w, ly), 1)

    # Create mask for rounded corners
    mask_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    mask_surface.fill((0, 0, 0, 0))

    # Draw the mask with selective rounded corners
    top_r = min(top_radius, h // 2, w // 2)
    bot_r = min(bottom_radius, h // 2, w // 2)

    # Main rectangle parts
    pygame.draw.rect(mask_surface, (255, 255, 255, 255),
                     (top_r, 0, w - 2 * top_r, top_r))  # Top middle
    pygame.draw.rect(mask_surface, (255, 255, 255, 255),
                     (0, top_r, w, h - top_r - bot_r))  # Middle
    pygame.draw.rect(mask_surface, (255, 255, 255, 255),
                     (bot_r, h - bot_r, w - 2 * bot_r, bot_r))  # Bottom middle

    # Top corners
    if top_r > 0:
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (top_r, top_r), top_r)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (w - top_r, top_r), top_r)
    else:
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, w, 1))

    # Bottom corners
    if bot_r > 0:
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (bot_r, h - bot_r), bot_r)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (w - bot_r, h - bot_r), bot_r)
    else:
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, h - 1, w, 1))

    # Apply mask to checkered pattern
    temp_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Blit to main surface
    surface.blit(temp_surface, (x, y))


def draw_checkered_content_area(surface, rect, header_height, corner_radius=12, cell_size=18,
                                 border_color=(100, 150, 130), border_width=2):
    """Draw the content area with checkered background, rounded corners, and border.

    This draws the entire content area with:
    - Checkered pattern extending under the header to fill rounded corners
    - Rounded corners at top and bottom
    - Border around the checkered area (below header)

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the entire window
        header_height: Height of the header (border starts below this)
        corner_radius: Radius for rounded corners
        cell_size: Size of each grid cell
        border_color: Color of the border around checkered area
        border_width: Width of the border (default 2)
    """
    x, y, w, h = rect

    # Draw checkered background starting AT header boundary
    # with rounded top corners visible (not covered by header)
    content_y = header_height
    content_h = h - header_height

    # Fill corner gaps with header color so they show through rounded corners
    header_color = (254, 211, 113)
    # Left corner fill
    pygame.draw.rect(surface, header_color, (x, content_y, corner_radius, corner_radius))
    # Right corner fill
    pygame.draw.rect(surface, header_color, (x + w - corner_radius, content_y, corner_radius, corner_radius))

    draw_checkered_background_rounded(
        surface,
        (x, content_y, w, content_h),
        cell_size=cell_size,
        top_radius=corner_radius,
        bottom_radius=corner_radius
    )

    # Draw border with rounded corners at TOP and BOTTOM
    bx, by, bw, bh = x, content_y, w, content_h
    r = min(corner_radius, bh // 2, bw // 2)

    # Create a temporary surface for the border
    border_surface = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Draw all four edges and corners
    for thickness in range(border_width):
        # Top edge (between top corners)
        pygame.draw.line(border_surface, border_color, (r, thickness), (bw - r, thickness), 1)
        # Bottom edge (between bottom corners)
        pygame.draw.line(border_surface, border_color, (r, bh - 1 - thickness), (bw - r, bh - 1 - thickness), 1)
        # Left edge (between corners)
        pygame.draw.line(border_surface, border_color, (thickness, r), (thickness, bh - r), 1)
        # Right edge (between corners)
        pygame.draw.line(border_surface, border_color, (bw - 1 - thickness, r), (bw - 1 - thickness, bh - r), 1)

    # All four corner arcs
    for thickness in range(border_width):
        # Top-left corner
        pygame.draw.arc(border_surface, border_color,
                       (thickness, thickness, (r - thickness) * 2, (r - thickness) * 2),
                       math.pi / 2, math.pi, 1)
        # Top-right corner
        pygame.draw.arc(border_surface, border_color,
                       (bw - r * 2 + thickness, thickness, (r - thickness) * 2, (r - thickness) * 2),
                       0, math.pi / 2, 1)
        # Bottom-left corner
        pygame.draw.arc(border_surface, border_color,
                       (thickness, bh - r * 2 + thickness, (r - thickness) * 2, (r - thickness) * 2),
                       math.pi, 3 * math.pi / 2, 1)
        # Bottom-right corner
        pygame.draw.arc(border_surface, border_color,
                       (bw - r * 2 + thickness, bh - r * 2 + thickness, (r - thickness) * 2, (r - thickness) * 2),
                       3 * math.pi / 2, 2 * math.pi, 1)

    surface.blit(border_surface, (bx, by))
