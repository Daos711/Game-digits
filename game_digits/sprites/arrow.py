import pygame


class Arrow(pygame.sprite.Sprite):
    # Кэш для изображений стрелок по направлениям
    arrow_images = {}

    def __init__(self, direction, position, game, tile):
        super().__init__()
        self.game = game
        self.tile = tile
        self.direction = direction
        self.image = self.get_arrow_image(direction)
        self.rect = self.image.get_rect(topleft=position)

    @classmethod
    def get_arrow_image(cls, direction):
        if direction in cls.arrow_images:
            return cls.arrow_images[direction].copy()

        # Создаем базовую стрелку
        image = pygame.Surface((65, 65), pygame.SRCALPHA)

        # Цвета
        arrow_color = (94, 150, 233)  # Основной цвет стрелки
        white_color = (255, 255, 255)  # Белая обводка (внутренняя)
        gray_color = (173, 179, 179)  # Серая обводка (внешняя)

        # Точки стрелки (прямоугольная часть уже, основание треугольника уже)
        points = [(20, 38), (40, 38), (40, 43), (49, 32), (40, 21), (40, 26), (20, 26)]

        # Рисуем серую обводку (внешняя)
        pygame.draw.lines(image, gray_color, True, points, 7)
        # Круги на углах для серой обводки
        for point in points:
            pygame.draw.circle(image, gray_color, point, 3)
        # Рисуем белую обводку (внутренняя)
        pygame.draw.lines(image, white_color, True, points, 4)
        # Круги на углах для белой обводки
        for point in points:
            pygame.draw.circle(image, white_color, point, 2)
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
