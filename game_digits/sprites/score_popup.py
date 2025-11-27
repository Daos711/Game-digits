import pygame

TILE_SIZE = 64
GAP = 3


class ScorePopup(pygame.sprite.Sprite):
    """Анимированное число очков, появляющееся при удалении плиток."""

    def __init__(self, value, position, delay, max_value, group=None, board=None):
        """
        Args:
            value: Значение очков (+1, +2, и т.д.)
            position: Позиция на сетке (row, col)
            delay: Задержка появления в миллисекундах
            max_value: Максимальное значение в последовательности
            group: Ссылка на группу для динамического расчёта яркости
            board: Ссылка на игровое поле для проверки появления плиток
        """
        super().__init__()
        self.value = value
        self.grid_position = position
        self.delay = delay
        self.max_value = max_value
        self.group = group
        self.board = board
        self.created_at = pygame.time.get_ticks()
        self.visible = False
        self.appeared_at = None
        self.alpha = 255  # Текущая прозрачность
        self.fade_speed = 1.5  # Скорость затухания за кадр для завершающего fadeout
        self.all_appeared = False  # Флаг что все цифры появились

        # Базовый цвет - тёмно-серый для контраста
        self.base_color = (80, 80, 80)

        # Создаём изображение с тонким шрифтом
        self.font = pygame.font.SysFont('arial', 36, bold=False)
        self.base_image = self.font.render(f"+{value}", True, self.base_color)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()

        # Позиционируем на сетке
        col, row = position[1], position[0]
        self.rect.centerx = (col + 1) * GAP + col * TILE_SIZE + TILE_SIZE // 2
        self.rect.centery = (row + 1) * GAP + row * TILE_SIZE + TILE_SIZE // 2

    def _count_visible_after_me(self):
        """Подсчитывает сколько цифр с большим value уже видимы."""
        if not self.group:
            return 0
        count = 0
        for popup in self.group:
            if popup.value > self.value and popup.visible:
                count += 1
        return count

    def _check_all_appeared(self):
        """Проверяет, появились ли все цифры в последовательности."""
        if not self.group:
            return True
        for popup in self.group:
            if not popup.visible:
                return False
        return True

    def update(self):
        """Обновляет состояние спрайта."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.created_at

        # Проверяем, пора ли появиться
        if not self.visible and elapsed >= self.delay:
            self.visible = True
            self.appeared_at = current_time

        if not self.visible:
            return

        # Проверяем, появилась ли плитка на нашей позиции
        if self.board is not None:
            row, col = self.grid_position
            if self.board[row][col] is not None:
                self.kill()
                return

        # Проверяем, появились ли все цифры
        if not self.all_appeared:
            self.all_appeared = self._check_all_appeared()

        # Вычисляем целевую прозрачность
        if self.all_appeared:
            # Все появились - плавно затухаем
            self.alpha = max(0, self.alpha - self.fade_speed)
        else:
            # Динамическая яркость: чем больше цифр появилось после нас, тем тусклее
            visible_after = self._count_visible_after_me()
            # Каждая следующая цифра уменьшает нашу яркость
            # При 0 цифр после нас - 255, при max_value-value цифр - минимум
            max_after = self.max_value - self.value
            if max_after > 0:
                fade_per_number = 230 / max_after  # Уменьшаем на ~230 к полному появлению
                target_alpha = max(25, 255 - int(visible_after * fade_per_number))
            else:
                target_alpha = 255
            # Плавно переходим к целевой прозрачности (быстрее затухаем)
            if self.alpha > target_alpha:
                self.alpha = max(target_alpha, self.alpha - 20)
            elif self.alpha < target_alpha:
                self.alpha = min(target_alpha, self.alpha + 8)

        # Удаляем если полностью прозрачны
        if self.alpha <= 0:
            self.kill()
            return

        # Обновляем изображение с новой прозрачностью
        self.image = self.base_image.copy()
        self.image.set_alpha(int(self.alpha))

    def draw(self, surface):
        """Рисует спрайт если он видим."""
        if self.visible and self.alpha > 0:
            surface.blit(self.image, self.rect)
