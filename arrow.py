import pygame


class Arrow(pygame.sprite.Sprite):
    # Кэш для изображений стрелок по направлениям
    arrow_images = {}

    def __init__(self, direction, position, game, tile, color=(101, 151, 237), border_color=(220, 220, 220)):
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
        points = [(20, 40), (40, 40), (40, 45), (49, 32), (40, 19), (40, 24), (20, 24)]
        pygame.draw.polygon(image, (101, 151, 237), points)
        pygame.draw.lines(image, (220, 220, 220), True, points, 3)

        # Вращаем изображение в зависимости от направления
        if direction == 'up':
            image = pygame.transform.rotate(image, 90)
        elif direction == 'down':
            image = pygame.transform.rotate(image, -90)
        elif direction == 'left':
            image = pygame.transform.rotate(image, 180)
        # 'right' не требует вращения

        cls.arrow_images[direction] = image
        return image.copy()