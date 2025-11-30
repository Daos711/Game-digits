import pygame
import pygame.gfxdraw


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

        # Цвета с оригинала (пипеткой)
        fill_color = (127, 157, 214)       # Основной синий цвет заливки
        dark_outline = (100, 106, 115)     # Тёмно-серая внутренняя обводка
        light_outline = (250, 250, 252)    # Светлый внешний кант

        image = pygame.Surface((65, 65), pygame.SRCALPHA)

        # Изящная тонкая стрелка (как в оригинале)
        # Центр по вертикали = 32
        center_y = 32

        # Хвост: узкий (высота ~7px)
        tail_half_height = 3
        tail_left = 14
        tail_right = 36

        # Крылья: выступают больше хвоста
        wing_half_height = 9

        # Острие
        tip_x = 52

        # Точки основной стрелки
        points = [
            (tail_left, center_y - tail_half_height),   # верх хвоста слева
            (tail_right, center_y - tail_half_height),  # верх хвоста справа
            (tail_right, center_y - wing_half_height),  # верхнее крыло
            (tip_x, center_y),                          # острие
            (tail_right, center_y + wing_half_height),  # нижнее крыло
            (tail_right, center_y + tail_half_height),  # низ хвоста справа
            (tail_left, center_y + tail_half_height),   # низ хвоста слева
        ]

        # Функция для смещения точек (для обводок)
        def offset_points(pts, offset):
            """Смещает точки наружу для создания обводки."""
            result = []
            for i, (x, y) in enumerate(pts):
                # Вычисляем направление смещения
                if x == tail_left:
                    # Левый край - смещаем влево
                    new_x = x - offset
                elif x == tip_x:
                    # Острие - смещаем вправо
                    new_x = x + offset
                else:
                    new_x = x

                if y < center_y:
                    new_y = y - offset
                elif y > center_y:
                    new_y = y + offset
                else:
                    new_y = y
                result.append((new_x, new_y))
            return result

        # 1. Внешний светлый кант (самый большой контур)
        outer_points = offset_points(points, 2)
        pygame.gfxdraw.filled_polygon(image, outer_points, light_outline)
        pygame.gfxdraw.aapolygon(image, outer_points, light_outline)

        # 2. Тёмная обводка (средний контур)
        mid_points = offset_points(points, 1)
        pygame.gfxdraw.filled_polygon(image, mid_points, dark_outline)
        pygame.gfxdraw.aapolygon(image, mid_points, dark_outline)

        # 3. Основная синяя заливка (внутренний контур)
        pygame.gfxdraw.filled_polygon(image, points, fill_color)
        pygame.gfxdraw.aapolygon(image, points, fill_color)

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
