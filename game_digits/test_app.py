"""
Test mode application for mechanics testing.
Small board with 10 tiles (5 pairs).
"""
import sys
import pygame

from game_digits import get_image_path, get_font_path
from game_digits.constants import (
    TILE_SIZE, GAP, COLORS,
    grid_to_pixel, pixel_to_grid, pixel_to_grid_round, create_background_surface
)
from game_digits.test_game import TestGame, TEST_BOARD_SIZE
from game_digits.sprites import Arrow, ScorePopup
from game_digits import ui_components as ui


class TestGameApp:
    """Test mode app with smaller board (5x5) and 10 tiles."""

    def __init__(self):
        # Window size adjusted for smaller board
        self.board_size = TEST_BOARD_SIZE
        tile_area = self.board_size * TILE_SIZE + (self.board_size + 1) * GAP
        self.frame = 10
        self.window = tile_area + 2 * self.frame
        self.panel_width = 240
        self.WIDTH = self.window + 2 * self.frame + self.panel_width
        self.HEIGHT = self.window + 2 * self.frame

        self.speed = 1
        self.tile_size, self.gap = TILE_SIZE, GAP
        self.offset = (23, 23)
        self.COLORS = COLORS

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

        opensans = get_font_path("OpenSans-VariableFont_wdth,wght.ttf")
        self.font_bold_large = pygame.font.Font(opensans, 26)
        self.font_bold_medium = pygame.font.Font(opensans, 22)
        self.font_bold_value = pygame.font.Font(opensans, 36)

        self.is_paused = False
        self.pause_button_rect = None
        self.pause_start_time = 0
        self.total_pause_time = 0
        self.paused_progress = 1.0

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Test Mode - 10 Tiles")
        self.icon = pygame.image.load(get_image_path("icon.png"))
        pygame.display.set_icon(self.icon)

        self.grid_cell_size = 25
        self.grid_line_color = (200, 200, 200)

        self.arrows = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.score_popups = pygame.sprite.Group()

        self.game = TestGame(self.tiles, time_limit=60)

        tile_surface_size = tile_area
        self.tile_surface = pygame.Surface((tile_surface_size, tile_surface_size))
        self.background_texture = create_background_surface(tile_surface_size, tile_surface_size)
        self.tile_surface.blit(self.background_texture, (0, 0))

        # No auto-add tiles in test mode
        self.timer_running = False

        self.COUNTDOWN_EVENT = self.game.COUNTDOWN_EVENT
        self.TILE_APPEAR_EVENT = self.game.TILE_APPEAR_EVENT

        self.game.start_tile_appearance()

    def draw_background(self):
        self.screen.fill((255, 255, 255))

        for x in range(0, self.WIDTH + 1, self.grid_cell_size):
            pygame.draw.line(self.screen, self.grid_line_color, (x, 0), (x, self.HEIGHT), 1)
        for y in range(0, self.HEIGHT + 1, self.grid_cell_size):
            pygame.draw.line(self.screen, self.grid_line_color, (0, y), (self.WIDTH, y), 1)

        # Yellow border around tile area
        pygame.draw.rect(
            self.screen,
            (247, 204, 74),
            (self.frame, self.frame, self.window, self.window),
            self.frame,
        )

        # Blue panel on the right
        panel_x = self.window + 2 * self.frame
        pygame.draw.rect(
            self.screen,
            (62, 157, 203),
            (panel_x, 0, self.panel_width, self.HEIGHT),
        )

        self.screen.blit(self.tile_surface, (2 * self.frame, 2 * self.frame))
        self.draw_score_and_timer_window()

    def draw_score_and_timer_window(self):
        panel_x = self.window + 2 * self.frame
        padding = 15
        current_y = padding

        # Pause button
        button_width = 120
        button_height = 40
        button_x = panel_x + (self.panel_width - button_width) // 2
        self.pause_button_rect = ui.draw_pause_button(
            self.screen,
            (button_x, current_y, button_width, button_height),
            self.font_bold_medium,
            is_pressed=self.is_paused
        )
        current_y += button_height + 25

        # Time label
        time_label = self.font_bold_large.render("Время", True, (255, 255, 255))
        label_x = panel_x + (self.panel_width - time_label.get_width()) // 2
        self.screen.blit(time_label, (label_x, current_y))
        current_y += time_label.get_height() + 10

        icon_size = 50
        icon_x = panel_x + padding
        bar_x = icon_x + icon_size // 2
        bar_width = self.panel_width - padding - bar_x + panel_x
        bar_height = 44

        ui.draw_value_bar(
            self.screen,
            (bar_x, current_y + 3, bar_width, bar_height),
            self.game.current_time,
            self.font_bold_value
        )
        ui.draw_clock_icon(self.screen, (icon_x + icon_size // 2, current_y + icon_size // 2), icon_size)
        current_y += icon_size + 25

        # Score label
        score_label = self.font_bold_large.render("Очки", True, (255, 255, 255))
        label_x = panel_x + (self.panel_width - score_label.get_width()) // 2
        self.screen.blit(score_label, (label_x, current_y))
        current_y += score_label.get_height() + 10

        ui.draw_value_bar(
            self.screen,
            (bar_x, current_y + 3, bar_width, bar_height),
            self.game.score,
            self.font_bold_value
        )
        ui.draw_sun_icon(self.screen, (icon_x + icon_size // 2, current_y + icon_size // 2), icon_size)

    def show_result_window(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        window_width, window_height = 400, 300
        window_surface = pygame.Surface((window_width, window_height))
        window_surface.fill((255, 255, 255))
        pygame.draw.rect(
            window_surface, (0, 0, 0), (0, 0, window_width, window_height), 2
        )

        window_x = (self.WIDTH - window_width) // 2
        window_y = (self.HEIGHT - window_height) // 2

        title_font = pygame.font.Font(None, 48)
        label_font = pygame.font.Font(None, 36)

        is_victory = not self.game.game_over_flag or self.game.current_time > 0

        if is_victory:
            title_text = title_font.render("Test Complete!", True, (0, 128, 0))
        else:
            title_text = title_font.render("Time's up!", True, (200, 0, 0))

        remaining_time = round(self.game.current_time)
        bonus = 300 + 5 * remaining_time

        title_rect = title_text.get_rect(center=(window_width // 2, 50))
        window_surface.blit(title_text, title_rect)

        total_score = self.game.score + bonus

        result_label = label_font.render("Score:", True, (0, 0, 0))
        result_label_rect = result_label.get_rect(topleft=(50, 100))
        window_surface.blit(result_label, result_label_rect)

        result_value = label_font.render(str(self.game.score), True, (0, 0, 0))
        result_value_rect = result_value.get_rect(topright=(window_width - 50, 100))
        window_surface.blit(result_value, result_value_rect)

        bonus_label = label_font.render("Speed bonus:", True, (0, 0, 0))
        bonus_label_rect = bonus_label.get_rect(topleft=(50, 150))
        window_surface.blit(bonus_label, bonus_label_rect)

        bonus_value = label_font.render(str(bonus), True, (0, 0, 0))
        bonus_value_rect = bonus_value.get_rect(topright=(window_width - 50, 150))
        window_surface.blit(bonus_value, bonus_value_rect)

        total_label = label_font.render("Total:", True, (0, 0, 0))
        total_label_rect = total_label.get_rect(topleft=(50, 200))
        window_surface.blit(total_label, total_label_rect)

        total_value = label_font.render(str(total_score), True, (0, 0, 0))
        total_value_rect = total_value.get_rect(topright=(window_width - 50, 200))
        window_surface.blit(total_value, total_value_rect)

        self.screen.blit(window_surface, (window_x, window_y))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            pygame.time.delay(100)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()

            if self.pause_button_rect and self.pause_button_rect.collidepoint(pos):
                self.toggle_pause()
                return True

            if self.is_paused:
                return True

            if self.game.is_initializing:
                return True

            pos = (pos[0] - self.offset[0], pos[1] - self.offset[1])
            self.handle_mouse_click(pos)
        return True

    def toggle_pause(self):
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.pause_start_time = pygame.time.get_ticks()
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 0)
        else:
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.total_pause_time += pause_duration
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 1000)

    def handle_mouse_click(self, pos):
        for arrow in self.arrows:
            if arrow.rect.collidepoint(pos):
                tile = arrow.tile
                direction = arrow.direction
                old_row, old_col = tile.position
                target_rect = tile.target_move(direction, self.game.board)
                new_row, new_col = pixel_to_grid(target_rect.topleft[0], target_rect.topleft[1])
                total_cells = abs(new_row - old_row) + abs(new_col - old_col)
                tile.move_start_pos = tile.position
                tile.last_grid_pos = tile.position
                tile.cells_left_count = 0
                tile.total_cells_to_move = total_cells
                tile.move_animation_group = pygame.sprite.Group()
                tile.is_moving = True
                tile.current_direction = direction
                self.arrows.empty()
                return

        for tile in self.tiles:
            if tile.rect.collidepoint(pos):
                self.handle_tile_click(tile)
                break

    def handle_tile_click(self, tile):
        if tile.is_moving:
            return
        if self.game.selected_tile:
            if self.game.selected_tile == tile:
                return
            positions = self.game.remove_tiles(self.game.selected_tile, tile)
            if positions:
                self.arrows.empty()
                self.spawn_score_animation(positions)
                self.update_display()
                self.game.selected_tile = None
                return

        self.arrows.empty()
        self.game.select_tile(tile)
        self.draw_arrows_for_tile(tile)

    def spawn_score_animation(self, positions):
        delay_per_number = 80
        max_value = len(positions)
        animation_group = pygame.sprite.Group()
        for i, pos in enumerate(positions):
            value = i + 1
            delay = i * delay_per_number
            popup = ScorePopup(value, pos, delay, max_value, group=animation_group, board=self.game.board)
            animation_group.add(popup)
            self.score_popups.add(popup)

    def draw_arrows_for_tile(self, tile):
        arrow_grid_positions = []
        for direction in ["up", "down", "left", "right"]:
            if self.game.can_move(tile, direction):
                arrow_position = self.get_arrow_position(tile.rect.topleft, direction)
                self.arrows.add(Arrow(direction, arrow_position, self.game, tile))
                row, col = tile.position
                if direction == "up":
                    arrow_grid_positions.append((row - 1, col))
                elif direction == "down":
                    arrow_grid_positions.append((row + 1, col))
                elif direction == "left":
                    arrow_grid_positions.append((row, col - 1))
                elif direction == "right":
                    arrow_grid_positions.append((row, col + 1))

        self.remove_popups_at_positions(arrow_grid_positions)
        self.update_display()
        self.arrows.draw(self.tile_surface)

    def remove_popups_at_positions(self, grid_positions):
        for popup in list(self.score_popups):
            if popup.grid_position in grid_positions:
                popup.kill()

    def get_arrow_position(self, tile_position, direction):
        x, y = tile_position
        if direction == "up":
            return (x, y - self.tile_size - self.gap)
        elif direction == "down":
            return (x, y + self.tile_size + self.gap)
        elif direction == "left":
            return (x - self.tile_size - self.gap, y)
        elif direction == "right":
            return (x + self.tile_size + self.gap, y)

    def snap_to_grid(self, tile):
        grid_row, grid_col = pixel_to_grid_round(tile.rect.topleft[0], tile.rect.topleft[1])
        grid_col = max(0, min(self.board_size - 1, grid_col))
        grid_row = max(0, min(self.board_size - 1, grid_row))

        if self.game.board[grid_row][grid_col] is not None and self.game.board[grid_row][grid_col] != tile:
            grid_row, grid_col = tile.position[0], tile.position[1]

        new_rect_x, new_rect_y = grid_to_pixel(grid_row, grid_col)
        tile.rect.topleft = (new_rect_x, new_rect_y)
        self.finalize_move(tile)

    def finalize_move(self, tile):
        tile.is_moving = False
        tile.current_direction = None

        if hasattr(tile, 'last_grid_pos'):
            del tile.last_grid_pos
            del tile.move_start_pos
            del tile.cells_left_count
            del tile.total_cells_to_move
            del tile.move_animation_group

        old_x, old_y = tile.position
        new_x, new_y = pixel_to_grid(tile.rect.topleft[0], tile.rect.topleft[1])
        tile.position = (new_x, new_y)
        self.game.update_board((old_x, old_y), (new_x, new_y), tile)

        if self.game.selected_tile == tile:
            self.game.deselect_tile()
            self.arrows.empty()

        delta_x = abs(new_x - old_x)
        delta_y = abs(new_y - old_y)
        cells_moved = delta_x + delta_y
        if cells_moved > 0:
            self.game.deduct_score(cells_moved)

        self.update_display()
        pygame.display.flip()

    def move_tile(self, tile, direction):
        target_rect = tile.target_move(direction, self.game.board)
        dx = target_rect.topleft[0] - tile.rect.topleft[0]
        dy = target_rect.topleft[1] - tile.rect.topleft[1]

        if dx == 0:
            step_y = self.speed * (1 if dy > 0 else -1)
            tile.rect.y += step_y
        elif dy == 0:
            step_x = self.speed * (1 if dx > 0 else -1)
            tile.rect.x += step_x

        if hasattr(tile, 'last_grid_pos'):
            current_row, current_col = pixel_to_grid(tile.rect.centerx, tile.rect.centery)
            current_pos = (current_row, current_col)
            if current_pos != tile.last_grid_pos:
                tile.cells_left_count += 1
                left_pos = tile.last_grid_pos
                popup = ScorePopup(
                    tile.cells_left_count, left_pos, 0, tile.total_cells_to_move,
                    group=tile.move_animation_group,
                    board=self.game.board,
                    negative=True
                )
                tile.move_animation_group.add(popup)
                self.score_popups.add(popup)
                tile.last_grid_pos = current_pos

        self.update_display()

    def update_display(self):
        self.tile_surface.blit(self.background_texture, (0, 0))
        self.tiles.draw(self.tile_surface)
        self.score_popups.update()
        for popup in self.score_popups:
            popup.draw(self.tile_surface)
        self.arrows.draw(self.tile_surface)
        self.draw_background()
        pygame.display.update()

    def run(self):
        running = True
        show_result = False
        prepare_to_show_result = False

        while running:
            self.tile_surface.blit(self.background_texture, (0, 0))
            self.tiles.draw(self.tile_surface)

            if not self.is_paused:
                self.score_popups.update()
            for popup in self.score_popups:
                popup.draw(self.tile_surface)

            self.arrows.draw(self.tile_surface)
            self.draw_background()

            if not self.is_paused:
                for tile in self.tiles:
                    if tile.is_moving:
                        direction = tile.current_direction
                        if direction:
                            self.move_tile(tile, direction)
                            target_rect = tile.target_move(direction, self.game.board)
                            dx = abs(tile.rect.x - target_rect.x)
                            dy = abs(tile.rect.y - target_rect.y)
                            if dx < 1 and dy < 1:
                                tile.rect.topleft = target_rect.topleft
                                self.finalize_move(tile)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == self.TILE_APPEAR_EVENT:
                    self.game.spawn_next_tile()
                    self.update_display()
                elif event.type == self.COUNTDOWN_EVENT:
                    self.game.handle_countdown()
                else:
                    running = self.handle_event(event)

            if self.game.prepare_to_end:
                self.game.prepare_to_end = False
                prepare_to_show_result = True
            elif prepare_to_show_result:
                prepare_to_show_result = False
                show_result = True

            if self.game.game_over_flag:
                show_result = True

            if show_result and not any(tile.is_moving for tile in self.tiles):
                self.score_popups.empty()
                self.update_display()
                pygame.display.flip()
                self.show_result_window()
                running = False
