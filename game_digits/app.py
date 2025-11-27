import sys
import pygame

from game_digits import get_image_path
from game_digits.game import Game
from game_digits.sprites import Arrow

TILE_SIZE = 64
GAP = 3


class GameApp:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 953, 713
        self.frame = 10
        self.speed = 1
        self.window = self.HEIGHT - 20
        self.panel_width, self.panel_height = 240, self.HEIGHT
        self.tile_size, self.gap = TILE_SIZE, GAP
        self.offset = (23, 23)
        self.COLORS = {
            1: (250, 130, 124),
            2: (98, 120, 255),
            3: (249, 204, 122),
            4: (127, 254, 138),
            5: (251, 94, 223),
            6: (126, 253, 205),
            7: (239, 255, 127),
            8: (174, 121, 251),
            9: (255, 152, 123),
        }
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Игра цифры")
        self.icon = pygame.image.load(get_image_path("icon.png"))
        pygame.display.set_icon(self.icon)
        self.background_tile = pygame.image.load(get_image_path("cell.JPG"))
        self.arrows = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.game = Game(self.tiles)
        self.tile_surface = pygame.Surface(
            (self.HEIGHT - 4 * self.frame, self.HEIGHT - 4 * self.frame)
        )
        self.tile_surface.fill((249, 246, 247))
        self.ADD_TILE_EVENT = pygame.USEREVENT + 1
        self.tile_timer_interval = 10500
        self.timer_running = False
        self.COUNTDOWN_EVENT = self.game.COUNTDOWN_EVENT

    def draw_background(self):
        for i in range(0, 960, self.background_tile.get_width()):
            for j in range(0, 720, self.background_tile.get_height()):
                self.screen.blit(self.background_tile, (i, j))
        pygame.draw.rect(
            self.screen,
            (247, 204, 74),
            (self.frame, self.frame, self.window, self.window),
            self.frame,
        )
        pygame.draw.rect(
            self.screen,
            (62, 157, 203),
            (self.HEIGHT, 0, self.panel_width, self.panel_height),
        )
        self.screen.blit(self.tile_surface, (2 * self.frame, 2 * self.frame))
        self.draw_score_and_timer_window()

    def draw_score_and_timer_window(self):
        # Окно счётчика очков
        score_window_rect = pygame.Rect(
            self.HEIGHT + 10, 10, self.panel_width - 20, 100
        )
        pygame.draw.rect(self.screen, (255, 255, 255), score_window_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), score_window_rect, 2)

        score_label = self.font.render("Очки", True, (0, 0, 0))
        label_rect = score_label.get_rect(
            center=(score_window_rect.centerx, score_window_rect.top + 20)
        )
        self.screen.blit(score_label, label_rect)

        score_text = self.font.render(str(self.game.score), True, (0, 0, 0))
        score_rect = score_text.get_rect(
            center=(score_window_rect.centerx, score_window_rect.top + 60)
        )
        self.screen.blit(score_text, score_rect)

        # Окно таймера
        time_window_rect = pygame.Rect(
            self.HEIGHT + 10, 120, self.panel_width - 20, 100
        )
        pygame.draw.rect(self.screen, (255, 255, 255), time_window_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), time_window_rect, 2)

        time_label = self.font.render("Время", True, (0, 0, 0))
        label_rect = time_label.get_rect(
            center=(time_window_rect.centerx, time_window_rect.top + 20)
        )
        self.screen.blit(time_label, label_rect)

        time_text = self.font.render(f"{self.game.current_time}", True, (0, 0, 0))
        time_rect = time_text.get_rect(
            center=(time_window_rect.centerx, time_window_rect.top + 60)
        )
        self.screen.blit(time_text, time_rect)

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
        title_text = title_font.render("Результат игры", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(window_width // 2, 50))
        window_surface.blit(title_text, title_rect)

        remaining_time = int(self.game.current_time)
        bonus = remaining_time * 5 + 300
        total_score = self.game.score + bonus

        label_font = pygame.font.Font(None, 36)
        result_label = label_font.render("Ваш результат:", True, (0, 0, 0))
        result_label_rect = result_label.get_rect(topleft=(50, 100))
        window_surface.blit(result_label, result_label_rect)

        result_value = label_font.render(str(self.game.score), True, (0, 0, 0))
        result_value_rect = result_value.get_rect(topright=(window_width - 50, 100))
        window_surface.blit(result_value, result_value_rect)

        bonus_label = label_font.render("Бонус за скорость:", True, (0, 0, 0))
        bonus_label_rect = bonus_label.get_rect(topleft=(50, 150))
        window_surface.blit(bonus_label, bonus_label_rect)

        bonus_value = label_font.render(str(bonus), True, (0, 0, 0))
        bonus_value_rect = bonus_value.get_rect(topright=(window_width - 50, 150))
        window_surface.blit(bonus_value, bonus_value_rect)

        total_label = label_font.render("Итого:", True, (0, 0, 0))
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
            pos = (pos[0] - self.offset[0], pos[1] - self.offset[1])
            self.handle_mouse_click(pos)
        return True

    def handle_mouse_click(self, pos):
        for arrow in self.arrows:
            if arrow.rect.collidepoint(pos):
                tile = arrow.tile
                tile.is_moving = True
                tile.current_direction = arrow.direction
                self.arrows.empty()
                return
        for tile in self.tiles:
            if tile.rect.collidepoint(pos):
                self.handle_tile_click(tile)
                break

    def handle_tile_click(self, tile):
        if self.game.selected_tile:
            if self.game.selected_tile == tile:
                return
            elif self.game.remove_tiles(self.game.selected_tile, tile):
                self.update_display()
                self.game.selected_tile = None
                if not self.timer_running and any(
                    self.game.board[i][j] is None for i in range(10) for j in range(10)
                ):
                    pygame.time.set_timer(self.ADD_TILE_EVENT, self.tile_timer_interval)
                    self.timer_running = True
                return
        self.arrows.empty()
        self.game.select_tile(tile)
        self.draw_arrows_for_tile(tile)

    def draw_arrows_for_tile(self, tile):
        for direction in ["up", "down", "left", "right"]:
            if self.game.can_move(tile, direction):
                arrow_position = self.get_arrow_position(tile.rect.topleft, direction)
                self.arrows.add(Arrow(direction, arrow_position, self.game, tile))
        self.update_display()
        self.arrows.draw(self.tile_surface)

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
        self.update_display()

    def finalize_move(self, tile):
        tile.is_moving = False
        tile.current_direction = None
        old_x, old_y = tile.position
        new_x = (tile.rect.topleft[1] - self.gap) // (self.tile_size + self.gap)
        new_y = (tile.rect.topleft[0] - self.gap) // (self.tile_size + self.gap)
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

    def update_display(self):
        self.tile_surface.fill((249, 246, 247))
        self.tiles.draw(self.tile_surface)
        self.draw_background()
        pygame.display.update()

    def run(self):
        running = True
        show_result = False
        prepare_to_show_result = False
        while running:
            self.draw_background()
            self.tiles.draw(self.tile_surface)
            for tile in self.tiles:
                if tile.is_moving:
                    direction = tile.current_direction
                    if direction:
                        self.move_tile(tile, direction)
                        target_rect = tile.target_move(direction, self.game.board)
                        if tile.rect.topleft == target_rect.topleft:
                            self.finalize_move(tile)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == self.ADD_TILE_EVENT:
                    self.game.add_new_tile()
                    self.update_display()
                    empty = any(
                        self.game.board[i][j] is None
                        for i in range(10)
                        for j in range(10)
                    )
                    if not empty:
                        pygame.time.set_timer(self.ADD_TILE_EVENT, 0)
                        self.timer_running = False
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
            if show_result and not any(tile.is_moving for tile in self.tiles):
                self.update_display()
                pygame.display.flip()
                self.show_result_window()
                running = False
