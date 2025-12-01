"""Start menu for the game."""
import sys
import math
import pygame

from game_digits import get_font_path
from game_digits.constants import COLORS, TILE_SIZE, TILE_BORDER_COLOR
from game_digits import ui_components as ui


class MenuTile:
    """A tile displaying a letter for the menu title."""

    def __init__(self, letter, color, target_x, target_y):
        self.letter = letter
        self.color = color
        self.target_x = target_x
        self.target_y = target_y
        self.x = -TILE_SIZE - 50  # Start off-screen left
        self.y = target_y
        self.velocity = 0

        # Create tile surface
        self.surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self._draw_tile()

    def _draw_tile(self):
        """Draw the tile with letter."""
        self.surface.fill(self.color)

        # 3D bevel effect
        bevel = 3
        dark_factor = 0.4
        dark = tuple(max(0, min(255, int(c * dark_factor))) for c in self.color)

        w, h = self.surface.get_size()

        # Bottom shadow
        pygame.draw.rect(self.surface, dark, (0, h - bevel, w, bevel))
        # Right shadow
        pygame.draw.rect(self.surface, dark, (w - bevel, 0, bevel, h))

        # Border
        pygame.draw.rect(self.surface, TILE_BORDER_COLOR, self.surface.get_rect(), 1)

        # Letter
        font = pygame.font.Font(get_font_path("OpenSans-VariableFont_wdth,wght.ttf"), 40)
        text = font.render(self.letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=(w // 2, h // 2))
        self.surface.blit(text, text_rect)

    def draw(self, surface):
        """Draw tile at current position."""
        surface.blit(self.surface, (int(self.x), int(self.y)))


class StartMenu:
    """Start menu with animated title tiles."""

    # Animation constants
    TILE_DELAY = 80  # ms between each tile animation start
    SPRING_STIFFNESS = 0.15  # Spring constant
    SPRING_DAMPING = 0.75  # Damping factor
    EXIT_SPEED = 15  # Pixels per frame when exiting
    EXIT_DELAY = 50  # ms between each tile exit
    BUTTON_FADE_DURATION = 300  # ms for button fade

    def __init__(self, screen, screen_size, redraw_background):
        self.screen = screen
        self.screen_width, self.screen_height = screen_size
        self.redraw_background = redraw_background

        # Load fonts
        bold_font_path = get_font_path("2204.ttf")
        self.button_font = pygame.font.Font(bold_font_path, 28)

        # Title letters and colors (using game tile colors)
        letters = ['Ц', 'И', 'Ф', 'Р', 'Ы']
        tile_colors = [
            COLORS[1],  # Pink/red
            COLORS[2],  # Blue
            COLORS[3],  # Yellow
            COLORS[4],  # Green
            COLORS[8],  # Purple
        ]

        # Calculate tile positions (centered on game field)
        # Game field is roughly 693x693, starting at (20, 20)
        field_center_x = 20 + 693 // 2
        field_center_y = 20 + 693 // 2 - 50  # Slightly above center

        total_width = len(letters) * TILE_SIZE + (len(letters) - 1) * 8  # 8px gap
        start_x = field_center_x - total_width // 2

        # Create tiles
        self.tiles = []
        for i, (letter, color) in enumerate(zip(letters, tile_colors)):
            x = start_x + i * (TILE_SIZE + 8)
            y = field_center_y - TILE_SIZE // 2
            self.tiles.append(MenuTile(letter, color, x, y))

        # Button setup
        button_width = 200
        button_height = 50
        self.button_rect = pygame.Rect(
            field_center_x - button_width // 2,
            field_center_y + TILE_SIZE // 2 + 40,
            button_width,
            button_height
        )

        # State
        self.state = 'entering'  # 'entering', 'idle', 'exiting'
        self.animation_start_time = 0
        self.button_pressed = False
        self.button_opacity = 0
        self.tiles_arrived = [False] * len(self.tiles)

    def _spring_physics(self, tile, index):
        """Apply spring physics to move tile to target position."""
        # Calculate spring force
        displacement = tile.target_x - tile.x
        spring_force = displacement * self.SPRING_STIFFNESS

        # Apply force and damping
        tile.velocity += spring_force
        tile.velocity *= self.SPRING_DAMPING
        tile.x += tile.velocity

        # Check if arrived (close enough and slow enough)
        if abs(displacement) < 1 and abs(tile.velocity) < 0.5:
            tile.x = tile.target_x
            tile.velocity = 0
            return True
        return False

    def _update_entering(self, current_time):
        """Update animation for entering state."""
        elapsed = current_time - self.animation_start_time

        all_arrived = True
        for i, tile in enumerate(self.tiles):
            # Stagger tile start times
            tile_start_time = i * self.TILE_DELAY
            if elapsed >= tile_start_time:
                arrived = self._spring_physics(tile, i)
                self.tiles_arrived[i] = arrived
                if not arrived:
                    all_arrived = False
            else:
                all_arrived = False

        # Update button opacity once tiles start arriving
        if any(self.tiles_arrived):
            button_start = len(self.tiles) * self.TILE_DELAY
            button_elapsed = max(0, elapsed - button_start)
            self.button_opacity = min(255, int(255 * button_elapsed / self.BUTTON_FADE_DURATION))

        if all_arrived and self.button_opacity >= 255:
            self.state = 'idle'

    def _update_exiting(self, current_time):
        """Update animation for exiting state."""
        elapsed = current_time - self.animation_start_time

        all_exited = True
        for i, tile in enumerate(self.tiles):
            # Stagger tile exit times
            tile_start_time = i * self.EXIT_DELAY
            if elapsed >= tile_start_time:
                tile.x += self.EXIT_SPEED
                if tile.x < self.screen_width + TILE_SIZE:
                    all_exited = False
            else:
                all_exited = False

        # Fade out button
        button_elapsed = elapsed
        self.button_opacity = max(0, 255 - int(255 * button_elapsed / self.BUTTON_FADE_DURATION))

        return all_exited

    def _draw(self):
        """Draw the menu."""
        # Draw background
        self.redraw_background()

        # Draw tiles
        for tile in self.tiles:
            tile.draw(self.screen)

        # Draw button with opacity
        if self.button_opacity > 0:
            # Create temporary surface for button with alpha
            btn_surface = pygame.Surface(
                (self.button_rect.width, self.button_rect.height),
                pygame.SRCALPHA
            )
            ui.draw_new_game_button(
                btn_surface,
                (0, 0, self.button_rect.width, self.button_rect.height),
                self.button_font,
                is_pressed=self.button_pressed,
                text="Начать игру"
            )
            btn_surface.set_alpha(self.button_opacity)
            self.screen.blit(btn_surface, self.button_rect.topleft)

        pygame.display.update()

    def reset_for_entry(self):
        """Reset tiles for entry animation (coming from left)."""
        for tile in self.tiles:
            tile.x = -TILE_SIZE - 50
            tile.velocity = 0
        self.tiles_arrived = [False] * len(self.tiles)
        self.button_opacity = 0
        self.state = 'entering'
        self.animation_start_time = pygame.time.get_ticks()

    def start_exit_animation(self):
        """Start the exit animation (tiles go right)."""
        self.state = 'exiting'
        self.animation_start_time = pygame.time.get_ticks()

    def show(self):
        """Display the menu and wait for user interaction.

        Returns:
            bool: True if user wants to start game, False to exit
        """
        self.reset_for_entry()

        running = True
        start_game = False

        while running:
            current_time = pygame.time.get_ticks()

            # Update animation
            if self.state == 'entering':
                self._update_entering(current_time)
            elif self.state == 'exiting':
                if self._update_exiting(current_time):
                    running = False
                    start_game = True

            # Draw
            self._draw()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.state == 'idle':
                    if self.button_rect.collidepoint(event.pos):
                        self.button_pressed = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.button_pressed and self.button_rect.collidepoint(event.pos):
                        self.start_exit_animation()
                    self.button_pressed = False
                elif event.type == pygame.KEYDOWN and self.state == 'idle':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.start_exit_animation()

            pygame.time.delay(16)  # ~60 FPS

        return start_game
