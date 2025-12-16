"""Confetti particle system for celebrations."""
import random
import pygame


class ConfettiParticle:
    """Single confetti particle."""

    COLORS = [
        (255, 107, 107),  # Красный
        (255, 193, 7),    # Жёлтый
        (76, 175, 80),    # Зелёный
        (33, 150, 243),   # Синий
        (156, 39, 176),   # Фиолетовый
        (255, 152, 0),    # Оранжевый
        (0, 188, 212),    # Голубой
        (233, 30, 99),    # Розовый
    ]

    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Размер частицы
        self.width = random.randint(6, 12)
        self.height = random.randint(4, 8)

        # Скорость
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(2, 6)

        # Вращение
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)

        # Цвет
        self.color = random.choice(self.COLORS)

        # Жизнь
        self.alive = True

    def update(self):
        """Update particle position."""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Гравитация
        self.angle += self.rotation_speed

        # Убираем если вышла за экран
        if self.y > self.screen_height + 50:
            self.alive = False

    def draw(self, surface):
        """Draw the particle."""
        # Создаём поверхность для частицы
        particle_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        particle_surf.fill(self.color)

        # Поворачиваем
        rotated = pygame.transform.rotate(particle_surf, self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))

        surface.blit(rotated, rect)


class ConfettiSystem:
    """Manages confetti particles."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles = []
        self.spawn_timer = 0
        self.spawning = False
        self.spawn_duration = 2000  # 2 секунды спавна
        self.spawn_start_time = 0

    def start(self):
        """Start spawning confetti."""
        self.spawning = True
        self.spawn_start_time = pygame.time.get_ticks()
        # Начальный взрыв частиц
        self._spawn_burst(100)

    def _spawn_burst(self, count):
        """Spawn a burst of particles."""
        for _ in range(count):
            x = random.randint(0, self.screen_width)
            y = random.randint(-50, 0)
            self.particles.append(
                ConfettiParticle(x, y, self.screen_width, self.screen_height)
            )

    def update(self):
        """Update all particles."""
        current_time = pygame.time.get_ticks()

        # Спавним новые частицы пока активно
        if self.spawning:
            elapsed = current_time - self.spawn_start_time
            if elapsed < self.spawn_duration:
                # Спавним каждые 50мс
                if current_time - self.spawn_timer > 50:
                    self._spawn_burst(5)
                    self.spawn_timer = current_time
            else:
                self.spawning = False

        # Обновляем частицы
        for particle in self.particles:
            particle.update()

        # Убираем мёртвые
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface)

    def is_active(self):
        """Check if there are still particles."""
        return self.spawning or len(self.particles) > 0
