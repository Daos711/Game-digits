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

        # Создаем базовую стрелку (направлена вправо)
        # Цвета по референсу
        fill_color = (127, 160, 216)      # #7FA0D8 - приглушённый синий
        inner_stroke = (144, 149, 156)    # #90959C - тёмно-серая внутренняя обводка
        outer_glow = (245, 245, 245)      # #F5F5F5 - светлый внешний ореол

        image = pygame.Surface((65, 65), pygame.SRCALPHA)

        # Тонкая аккуратная стрелка (хвост уже, кончик острее)
        # Стрелка направлена вправо, центрирована в 65x65
        # Хвост: узкий прямоугольник, наконечник: острый треугольник
        tail_top = 28
        tail_bottom = 37
        tail_left = 12
        tail_right = 38
        tip_x = 54
        tip_y = 32  # центр по вертикали
        wing_top = 22
        wing_bottom = 43

        # Точки стрелки (по часовой стрелке)
        points = [
            (tail_left, tail_top),      # верхний левый угол хвоста
            (tail_right, tail_top),     # верхний правый угол хвоста
            (tail_right, wing_top),     # верхнее крыло
            (tip_x, tip_y),             # острие
            (tail_right, wing_bottom),  # нижнее крыло
            (tail_right, tail_bottom),  # нижний правый угол хвоста
            (tail_left, tail_bottom),   # нижний левый угол хвоста
        ]

        # Внешний ореол (рисуем сначала, он будет под основной стрелкой)
        pygame.draw.polygon(image, outer_glow, points)
        pygame.draw.lines(image, outer_glow, True, points, 4)

        # Основная заливка стрелки
        pygame.draw.polygon(image, fill_color, points)

        # Внутренняя тёмная обводка (1px)
        pygame.draw.lines(image, inner_stroke, True, points, 1)

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
