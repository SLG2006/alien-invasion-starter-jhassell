import pygame
from ship import Ship

class Scoreboard:
    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.stats = ai_game.stats
        self.settings = ai_game.settings
        self.font = pygame.font.SysFont(None, 48)
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_score(self):
        score_str = f"{self.stats.score:,}"
        self.score_image = self.font.render(score_str, True, (255, 255, 255), (0, 0, 0))
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_score(self):
        high_score = round(self.stats.high_score, -1)
        high_score_str = f"High: {high_score:,}"
        self.high_score_image = self.font.render(high_score_str, True, (255, 255, 255), (0, 0, 0))
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = 20

    def prep_level(self):
        level_str = f"Level {self.stats.level}"
        self.level_image = self.font.render(level_str, True, (255, 255, 255), (0, 0, 0))
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.screen_rect.right - 20
        self.level_rect.top = self.score_rect.bottom + 8

    def prep_ships(self):
        self.ships = pygame.sprite.Group()
        for i in range(self.stats.ships_left):
            ship = Ship(self.screen, self.settings)
            scale = 0.4
            w = int(ship.rect.width  * scale)
            h = int(ship.rect.height * scale)
            ship.image = pygame.transform.scale(ship.image, (w, h))
            ship.rect = ship.image.get_rect()
            ship.rect.x = 10 + i * (w + 8)
            ship.rect.y = 10
            self.ships.add(ship)

    def check_high_score(self):
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def show_score(self):
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)
