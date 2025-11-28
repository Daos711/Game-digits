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
        color_top = (220, 170, 50)      # Тёмно-жёлтый
        color_bottom = (200, 140, 30)   # Тёмно-оранжевый
    else:
        # Жёлто-оранжевый градиент (верх светлее, низ темнее)
        color_top = (255, 210, 80)      # Светло-жёлтый
        color_bottom = (250, 175, 50)   # Оранжевый

    # Рисуем кнопку с градиентом
    draw_gradient_rounded_rect(surface, rect, color_top, color_bottom, radius)

    # Белый жирный текст по центру с небольшой тенью
    # Тень текста
    shadow_text = font.render(text, True, (180, 120, 40))
    shadow_rect = shadow_text.get_rect(center=(x + w // 2 + 1, y + h // 2 + 1))
    surface.blit(shadow_text, shadow_rect)
    # Основной текст
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
    surface.blit(text_surface, text_rect)

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


def draw_badge(surface, rect, icon_type="clock"):
    """Draw a badge (skewed quadrilateral) with icon inside - like reference."""
    x, y, w, h = rect

    # Скошенный четырёхугольник (как наклейка)
    skew = 5  # Смещение для скоса
    points = [
        (x + skew, y),           # Верх-лево
        (x + w, y + skew),       # Верх-право
        (x + w - skew, y + h),   # Низ-право
        (x, y + h - skew),       # Низ-лево
    ]

    # Фон бейджа (тёмно-синий/серо-голубой как на референсе)
    badge_color = (70, 115, 160)
    border_color = (100, 145, 185)
    highlight_color = (130, 170, 210)

    # Заливка фона
    pygame.draw.polygon(surface, badge_color, points)

    # Светлая рамка сверху и слева (для объёма)
    pygame.draw.line(surface, highlight_color, points[0], points[1], 2)
    pygame.draw.line(surface, highlight_color, points[3], points[0], 2)

    # Тёмная рамка снизу и справа
    pygame.draw.line(surface, (50, 85, 120), points[1], points[2], 2)
    pygame.draw.line(surface, (50, 85, 120), points[2], points[3], 2)

    # Иконка внутри
    center = (x + w // 2, y + h // 2)
    icon_size = min(w, h) - 10

    if icon_type == "clock":
        draw_clock_icon(surface, center, icon_size)
    elif icon_type == "sun":
        draw_sun_icon(surface, center, icon_size)


def draw_value_bar(surface, rect, value, font):
    """Draw the blue value bar with number inside - like reference."""
    x, y, w, h = rect
    radius = 8  # Менее скруглённые углы

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
    """Draw progress bar with same style as value bars."""
    x, y, w, h = rect
    if radius is None:
        radius = 8  # Менее скруглённые углы как у value bar

    # Жёлто-оранжевый градиент (как у кнопки паузы)
    color_top = (255, 210, 80)
    color_bottom = (250, 175, 50)

    # Заполненная часть
    bar_width = int(w * progress)
    if bar_width > radius * 2:  # Минимальная ширина для отрисовки
        draw_gradient_rounded_rect(surface, (x, y, bar_width, h), color_top, color_bottom, radius)


def draw_mute_button(surface, pos, size, is_muted=False):
    """Draw mute/unmute speaker icon."""
    x, y = pos

    # Рисуем динамик
    speaker_color = (200, 200, 200)

    # Корпус динамика
    body_points = [
        (x, y + size // 3),
        (x + size // 3, y + size // 3),
        (x + size * 2 // 3, y),
        (x + size * 2 // 3, y + size),
        (x + size // 3, y + size * 2 // 3),
        (x, y + size * 2 // 3),
    ]
    pygame.draw.polygon(surface, speaker_color, body_points)

    if is_muted:
        # Крестик для muted
        pygame.draw.line(surface, (200, 50, 50), (x + size * 2 // 3 + 5, y + 5), (x + size, y + size - 5), 3)
        pygame.draw.line(surface, (200, 50, 50), (x + size * 2 // 3 + 5, y + size - 5), (x + size, y + 5), 3)
    else:
        # Волны звука
        for i in range(2):
            arc_x = x + size * 2 // 3 + 5 + i * 8
            pygame.draw.arc(surface, speaker_color,
                          (arc_x, y + size // 4, 10, size // 2),
                          -math.pi / 3, math.pi / 3, 2)

    return pygame.Rect(x, y, size, size)


def draw_section_label(surface, text, pos, font):
    """Draw section label (Время, Очки) in white bold."""
    text_surface = font.render(text, True, (255, 255, 255))
    surface.blit(text_surface, pos)
