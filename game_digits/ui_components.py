"""UI components for the right panel."""
import pygame
import math


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
    radius = 8  # Менее скруглённые углы

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
    pygame.draw.circle(surface, (200, 150, 40), (x, y), radius, 2)

    # Стрелки часов (тёмно-коричневые)
    hand_color = (80, 50, 20)

    # Часовая стрелка (короткая, указывает на ~10)
    hour_length = radius * 0.45
    hour_angle = math.radians(-120)  # 10 часов
    hour_end_x = x + hour_length * math.cos(hour_angle)
    hour_end_y = y + hour_length * math.sin(hour_angle)
    pygame.draw.line(surface, hand_color, (x, y), (hour_end_x, hour_end_y), 3)

    # Минутная стрелка (длинная, указывает на ~2)
    min_length = radius * 0.65
    min_angle = math.radians(-30)  # 2 часа
    min_end_x = x + min_length * math.cos(min_angle)
    min_end_y = y + min_length * math.sin(min_angle)
    pygame.draw.line(surface, hand_color, (x, y), (min_end_x, min_end_y), 2)

    # Центральная точка
    pygame.draw.circle(surface, hand_color, (x, y), 3)


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
    pygame.draw.circle(surface, (200, 140, 30), (x, y), radius, 2)


def draw_value_bar(surface, rect, value, font):
    """Draw the blue value bar with number inside - like reference."""
    x, y, w, h = rect
    radius = 4  # Более угловатые края

    # Голубой градиент (верх темнее, низ светлее - как на референсе)
    color_top = (70, 130, 175)
    color_bottom = (110, 170, 210)

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
        radius = 4  # Более угловатые края как у value bar

    # 1. Сначала рисуем синий фон (как у value bar)
    bg_color_top = (70, 130, 175)
    bg_color_bottom = (110, 170, 210)
    draw_gradient_rounded_rect(surface, rect, bg_color_top, bg_color_bottom, radius)

    # 2. Затем рисуем жёлтую заполненную часть поверх
    # Верхние 2/3 высоты - RGB(255, 192, 41), нижняя 1/3 - RGB(211, 136, 0)
    bar_width = int(w * progress)
    if bar_width > 0:  # Рисуем при любом положительном прогрессе
        # Адаптивный радиус скругления - уменьшается пропорционально ширине
        actual_radius = min(radius, bar_width // 2)

        # Создаём временную поверхность для двухцветной полоски
        temp_surface = pygame.Surface((bar_width, h), pygame.SRCALPHA)

        # Верхняя часть (2/3 высоты)
        upper_height = int(h * 2 / 3)
        upper_color = (255, 192, 41)
        pygame.draw.rect(temp_surface, upper_color, (0, 0, bar_width, upper_height))

        # Нижняя часть (1/3 высоты)
        lower_color = (211, 136, 0)
        pygame.draw.rect(temp_surface, lower_color, (0, upper_height, bar_width, h - upper_height))

        # Создаём маску для скруглённых углов (с адаптивным радиусом)
        mask_surface = pygame.Surface((bar_width, h), pygame.SRCALPHA)
        if actual_radius > 0:
            draw_rounded_rect(mask_surface, (255, 255, 255, 255), (0, 0, bar_width, h), actual_radius)
        else:
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, bar_width, h))

        # Применяем маску
        temp_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(temp_surface, (x, y))


def draw_result_window_header(surface, rect, title, font, close_callback_rect=None):
    """Draw the yellow header bar with title and close button.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the header
        title: Title text to display
        font: Font for the title
        close_callback_rect: If provided, will be set to the close button rect

    Returns:
        pygame.Rect of the close button
    """
    x, y, w, h = rect
    radius = 12

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

    # Close button - yellow circle with white X
    btn_radius = 14
    btn_x = x + w - btn_radius - 10
    btn_y = y + h // 2

    # Yellow circle (slightly darker than header)
    pygame.draw.circle(surface, (255, 200, 80), (btn_x, btn_y), btn_radius)
    pygame.draw.circle(surface, (200, 160, 60), (btn_x, btn_y), btn_radius, 2)

    # White X
    x_size = 6
    x_color = (255, 255, 255)
    pygame.draw.line(surface, x_color, (btn_x - x_size, btn_y - x_size),
                    (btn_x + x_size, btn_y + x_size), 3)
    pygame.draw.line(surface, x_color, (btn_x - x_size, btn_y + x_size),
                    (btn_x + x_size, btn_y - x_size), 3)

    return pygame.Rect(btn_x - btn_radius, btn_y - btn_radius, btn_radius * 2, btn_radius * 2)


def draw_result_row(surface, rect, label, value, label_font, value_font):
    """Draw a result row with blue background.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the row
        label: Text label (e.g., "Ваш результат:")
        value: Numeric value to display
        label_font: Font for the label
        value_font: Font for the value (larger)
    """
    x, y, w, h = rect
    radius = 6

    # Background - RGB(168, 212, 242)
    bg_color = (168, 212, 242)
    draw_rounded_rect(surface, bg_color, rect, radius)

    # Text color - RGB(40, 92, 120)
    text_color = (40, 92, 120)

    # Label on the left
    label_surface = label_font.render(label, True, text_color)
    label_rect = label_surface.get_rect(midleft=(x + 15, y + h // 2))
    surface.blit(label_surface, label_rect)

    # Value on the right (larger font)
    value_surface = value_font.render(str(value), True, text_color)
    value_rect = value_surface.get_rect(midright=(x + w - 15, y + h // 2))
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
    radius = 6

    # Background - RGB(255, 238, 196)
    bg_color = (255, 238, 196)
    draw_rounded_rect(surface, bg_color, rect, radius)

    # Text color - RGB(166, 63, 42)
    text_color = (166, 63, 42)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
    surface.blit(text_surface, text_rect)


def draw_checkered_background(surface, rect, cell_size=25):
    """Draw a checkered (grid) background like a school notebook.

    Args:
        surface: Pygame surface to draw on
        rect: (x, y, width, height) of the area
        cell_size: Size of each grid cell
    """
    x, y, w, h = rect

    # Fill with white
    pygame.draw.rect(surface, (255, 255, 255), rect)

    # Draw grid lines (light gray)
    line_color = (200, 210, 220)

    # Vertical lines
    for lx in range(x, x + w + 1, cell_size):
        pygame.draw.line(surface, line_color, (lx, y), (lx, y + h), 1)

    # Horizontal lines
    for ly in range(y, y + h + 1, cell_size):
        pygame.draw.line(surface, line_color, (x, ly), (x + w, ly), 1)
