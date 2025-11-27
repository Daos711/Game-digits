import pygame

TILE_SIZE = 64
GAP = 3


class ScorePopup(pygame.sprite.Sprite):
    """Анимированное число очков, появляющееся при удалении плиток."""

    def __init__(self, value, position, delay, max_value):
        """
        Args:
            value: Значение очков (+1, +2, и т.д.)
            position: Позиция на сетке (row, col)
            delay: Задержка появления в миллисекундах
            max_value: Максимальное значение в последовательности (для расчёта цвета)
        """
        super().__init__()
        self.value = value
        self.grid_position = position
        self.delay = delay
        self.max_value = max_value
        self.created_at = pygame.time.get_ticks()
        self.visible = False
        self.duration = 1500  # Время жизни после появления (мс)
        self.appeared_at = None

        # Вычисляем цвет (от светлого к тёмному)
        # Прогресс от 0 (первое число) до 1 (последнее)
        if max_value > 1:
            progress = (value - 1) / (max_value - 1)
        else:
            progress = 0

        # Светлый серый -> тёмный серый
        base_color = 200 - int(progress * 120)  # от 200 до 80
        self.color = (base_color, base_color, base_color)

        # Создаём изображение
        self.font = pygame.font.Font(None, 32)
        self.image = self.font.render(f"+{value}", True, self.color)
        self.rect = self.image.get_rect()

        # Позиционируем на сетке
        col, row = position[1], position[0]
        self.rect.centerx = (col + 1) * GAP + col * TILE_SIZE + TILE_SIZE // 2
        self.rect.centery = (row + 1) * GAP + row * TILE_SIZE + TILE_SIZE // 2

    def update(self):
        """Обновляет состояние спрайта."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.created_at

        # Проверяем, пора ли появиться
        if not self.visible and elapsed >= self.delay:
            self.visible = True
            self.appeared_at = current_time

        # Проверяем, пора ли исчезнуть
        if self.visible and self.appeared_at:
            if current_time - self.appeared_at >= self.duration:
                self.kill()

    def draw(self, surface):
        """Рисует спрайт если он видим."""
        if self.visible:
            surface.blit(self.image, self.rect)
