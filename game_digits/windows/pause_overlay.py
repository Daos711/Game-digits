"""
Animated pause overlay with multiple animation patterns.
"""

import math
import random
import pygame
from game_digits import get_font_path


class PauseTile:
    """A single animated tile for the pause screen."""

    def __init__(self, letter: str, color: tuple, x: float, y: float, tile_size: int = 52):
        self.letter = letter
        self.color = color
        self.tile_size = tile_size
        self.x = x
        self.y = y

        # For bounce pattern
        self.vx = 0
        self.vy = 0

        # Font for the letter
        self.font = pygame.font.Font(get_font_path("2204.ttf"), 32)

        # Pre-render the tile surface
        self._render_tile()

    def _render_tile(self):
        """Pre-render the tile with letter."""
        self.surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)

        radius = 8
        rect = pygame.Rect(0, 0, self.tile_size, self.tile_size)

        pygame.draw.rect(self.surface, self.color, rect, border_radius=radius)

        highlight = pygame.Surface((self.tile_size, self.tile_size // 2), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 40))
        self.surface.blit(highlight, (0, 0))

        border_color = tuple(max(0, c - 40) for c in self.color)
        pygame.draw.rect(self.surface, border_color, rect, width=2, border_radius=radius)

        text = self.font.render(self.letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.tile_size // 2, self.tile_size // 2))
        self.surface.blit(text, text_rect)

    def draw(self, surface: pygame.Surface):
        """Draw the tile at current position."""
        pos = (int(self.x - self.tile_size // 2), int(self.y - self.tile_size // 2))
        surface.blit(self.surface, pos)


class OrbitPattern:
    """Tiles orbit around center in elliptical paths."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y

        # Assign orbit parameters to each tile
        for i, tile in enumerate(tiles):
            tile.orbit_radius = 80 + (i % 2) * 30
            tile.orbit_speed = 0.5 + (i * 0.1)
            tile.phase = (i / len(tiles)) * 2 * math.pi

    def update(self, time_ms):
        for tile in self.tiles:
            angle = tile.phase + (time_ms / 1000.0) * tile.orbit_speed
            tile.x = self.center_x + math.cos(angle) * tile.orbit_radius
            tile.y = self.center_y + math.sin(angle) * tile.orbit_radius * 0.5


class BouncePattern:
    """DVD screensaver style - tiles bounce off edges."""

    def __init__(self, tiles, width, height):
        self.tiles = tiles
        self.width = width
        self.height = height
        self.margin = 30

        # Initialize positions and velocities
        for i, tile in enumerate(tiles):
            tile.x = width // 2 + (i - 2) * 60
            tile.y = height // 2
            angle = random.uniform(0, 2 * math.pi)
            speed = 2 + random.uniform(0, 1)
            tile.vx = math.cos(angle) * speed
            tile.vy = math.sin(angle) * speed

    def update(self, time_ms):
        for tile in self.tiles:
            tile.x += tile.vx
            tile.y += tile.vy

            half = tile.tile_size // 2
            if tile.x - half < self.margin or tile.x + half > self.width - self.margin:
                tile.vx = -tile.vx
                tile.x = max(self.margin + half, min(self.width - self.margin - half, tile.x))
            if tile.y - half < self.margin or tile.y + half > self.height - self.margin:
                tile.vy = -tile.vy
                tile.y = max(self.margin + half, min(self.height - self.margin - half, tile.y))


class WavePattern:
    """Tiles in a row with wave pulsing effect."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.base_spacing = 60

    def update(self, time_ms):
        t = time_ms / 1000.0
        total_width = (len(self.tiles) - 1) * self.base_spacing
        start_x = self.center_x - total_width / 2

        for i, tile in enumerate(self.tiles):
            tile.x = start_x + i * self.base_spacing
            # Wave motion - each tile has phase offset
            wave_offset = math.sin(t * 3 + i * 0.8) * 20
            tile.y = self.center_y + wave_offset
            # Scale effect (simulated by position jitter)
            scale_offset = math.sin(t * 2 + i * 0.5) * 5
            tile.y += scale_offset


class SnakePattern:
    """Tiles follow each other in a snake pattern."""

    def __init__(self, tiles, center_x, center_y, width, height):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height

        # Path history for snake following
        self.path = []
        self.head_x = center_x
        self.head_y = center_y
        self.angle = 0
        self.path_spacing = 30

    def update(self, time_ms):
        t = time_ms / 1000.0

        # Move head in a smooth wandering pattern
        self.angle += math.sin(t * 0.7) * 0.05 + math.cos(t * 1.1) * 0.03
        speed = 3
        self.head_x += math.cos(self.angle) * speed
        self.head_y += math.sin(self.angle) * speed

        # Bounce off walls
        margin = 80
        if self.head_x < margin:
            self.head_x = margin
            self.angle = math.pi - self.angle
        if self.head_x > self.width - margin:
            self.head_x = self.width - margin
            self.angle = math.pi - self.angle
        if self.head_y < margin:
            self.head_y = margin
            self.angle = -self.angle
        if self.head_y > self.height - margin:
            self.head_y = self.height - margin
            self.angle = -self.angle

        # Add to path
        self.path.append((self.head_x, self.head_y))

        # Keep path limited
        max_path = len(self.tiles) * self.path_spacing + 100
        if len(self.path) > max_path:
            self.path = self.path[-max_path:]

        # Position tiles along path
        for i, tile in enumerate(self.tiles):
            path_index = len(self.path) - 1 - i * self.path_spacing
            if path_index >= 0 and path_index < len(self.path):
                tile.x, tile.y = self.path[path_index]
            else:
                tile.x, tile.y = self.center_x, self.center_y


class SpiralPattern:
    """Tiles move in expanding/contracting spiral."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y

    def update(self, time_ms):
        t = time_ms / 1000.0

        for i, tile in enumerate(self.tiles):
            # Base angle for this tile
            base_angle = (i / len(self.tiles)) * 2 * math.pi

            # Rotating angle
            angle = base_angle + t * 0.8

            # Pulsing radius
            base_radius = 60 + i * 15
            pulse = math.sin(t * 1.5) * 30
            radius = base_radius + pulse

            tile.x = self.center_x + math.cos(angle) * radius
            tile.y = self.center_y + math.sin(angle) * radius


class PauseOverlay:
    """Animated overlay shown when game is paused.

    Randomly selects from multiple animation patterns.
    """

    COLORS = [
        (231, 125, 128),  # П - red/pink
        (111, 183, 214),  # А - blue
        (136, 189, 134),  # У - green
        (178, 161, 199),  # З - purple
        (245, 203, 105),  # А - yellow
    ]

    PATTERN_NAMES = ['orbit', 'bounce', 'wave', 'snake', 'spiral']

    def __init__(self, field_width: int, field_height: int):
        self.field_width = field_width
        self.field_height = field_height

        self.tiles = []
        self.pattern = None
        self.start_time = 0

        self.subtitle_font = pygame.font.Font(get_font_path("2204.ttf"), 24)

        self._create_tiles()

    def _create_tiles(self):
        """Create tile objects for ПАУЗА."""
        letters = "ПАУЗА"
        center_x = self.field_width // 2
        center_y = self.field_height // 2

        self.tiles = []
        for i, letter in enumerate(letters):
            tile = PauseTile(
                letter=letter,
                color=self.COLORS[i],
                x=center_x,
                y=center_y
            )
            self.tiles.append(tile)

    def _select_pattern(self):
        """Randomly select an animation pattern."""
        pattern_name = random.choice(self.PATTERN_NAMES)
        center_x = self.field_width // 2
        center_y = self.field_height // 2

        if pattern_name == 'orbit':
            self.pattern = OrbitPattern(self.tiles, center_x, center_y)
        elif pattern_name == 'bounce':
            self.pattern = BouncePattern(self.tiles, self.field_width, self.field_height)
        elif pattern_name == 'wave':
            self.pattern = WavePattern(self.tiles, center_x, center_y)
        elif pattern_name == 'snake':
            self.pattern = SnakePattern(self.tiles, center_x, center_y,
                                        self.field_width, self.field_height)
        elif pattern_name == 'spiral':
            self.pattern = SpiralPattern(self.tiles, center_x, center_y)

    def start(self):
        """Start the animation with a random pattern."""
        self.start_time = pygame.time.get_ticks()
        self._create_tiles()  # Reset tiles
        self._select_pattern()

    def update(self):
        """Update tile positions based on current pattern."""
        if self.pattern:
            current_time = pygame.time.get_ticks() - self.start_time
            self.pattern.update(current_time)

    def draw(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """Draw the pause overlay."""
        overlay = pygame.Surface((self.field_width, self.field_height), pygame.SRCALPHA)

        # Fully opaque dark background
        overlay.fill((35, 50, 65, 255))

        # Update and draw tiles
        self.update()
        for tile in self.tiles:
            tile.draw(overlay)

        # Draw subtitle
        subtitle = self.subtitle_font.render("Игра приостановлена", True, (140, 150, 160))
        subtitle_rect = subtitle.get_rect(center=(self.field_width // 2, self.field_height - 50))
        overlay.blit(subtitle, subtitle_rect)

        surface.blit(overlay, (offset_x, offset_y))
