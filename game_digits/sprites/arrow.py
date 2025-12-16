import pygame

from game_digits import scale as scale_module


class Arrow(pygame.sprite.Sprite):
    # Кэш для изображений стрелок по направлениям
    # Ключ включает размер для инвалидации при смене масштаба
    arrow_images = {}
    _cached_arrow_size = None

    def __init__(self, direction, position, game, tile):
        super().__init__()
        self.game = game
        self.tile = tile
        self.direction = direction
        self.image = self.get_arrow_image(direction)
        self.rect = self.image.get_rect(topleft=position)

    @classmethod
    def get_arrow_image(cls, direction):
        arrow_size = scale_module.ARROW_SIZE
        base_arrow_size = scale_module.BASE_ARROW_SIZE

        # Инвалидация кэша при изменении масштаба
        if cls._cached_arrow_size != arrow_size:
            cls.arrow_images.clear()
            cls._cached_arrow_size = arrow_size

        if direction in cls.arrow_images:
            return cls.arrow_images[direction].copy()

        # Коэффициент масштабирования
        scale_factor = arrow_size / base_arrow_size

        # Создаем базовую стрелку
        image = pygame.Surface((arrow_size, arrow_size), pygame.SRCALPHA)

        # Цвета
        arrow_color = (94, 150, 233)  # Основной цвет стрелки
        white_color = (255, 255, 255)  # Белая обводка (внутренняя)
        gray_color = (173, 179, 179)  # Серая обводка (внешняя)

        # Базовые точки стрелки (для размера 65x65)
        base_points = [(20, 38), (40, 38), (40, 43), (49, 32), (40, 21), (40, 26), (20, 26)]
        # Масштабируем точки
        points = [(int(x * scale_factor), int(y * scale_factor)) for x, y in base_points]

        # Масштабируем толщину линий и радиусы
        outer_line_width = max(1, int(7 * scale_factor))
        inner_line_width = max(1, int(4 * scale_factor))
        outer_circle_radius = max(1, int(3 * scale_factor))
        inner_circle_radius = max(1, int(2 * scale_factor))

        # Рисуем серую обводку (внешняя)
        pygame.draw.lines(image, gray_color, True, points, outer_line_width)
        # Круги на углах для серой обводки
        for point in points:
            pygame.draw.circle(image, gray_color, point, outer_circle_radius)
        # Рисуем белую обводку (внутренняя)
        pygame.draw.lines(image, white_color, True, points, inner_line_width)
        # Круги на углах для белой обводки
        for point in points:
            pygame.draw.circle(image, white_color, point, inner_circle_radius)
        # Рисуем заливку основным цветом
        pygame.draw.polygon(image, arrow_color, points)

        # Вращаем изображение в зависимости от направления
        if direction == "up":
            image = pygame.transform.rotate(image, 90)
        elif direction == "down":
            image = pygame.transform.rotate(image, -90)
        elif direction == "left":
            image = pygame.transform.rotate(image, 180)
        # 'right' не требует вращения

        cls.arrow_images[direction] = image
        return image.copy()
