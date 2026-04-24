import time
import pygame
import random
from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from alien_bullet import AlienBullet
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Alien Invasion")
        self.clock = pygame.time.Clock()
        self.dots = [(random.randint(0, 800), random.randint(0, 600)) for _ in range(150)]
        self.stats = GameStats(self)
        self.play_button = Button(self, 'Play')
        self.sb = Scoreboard(self)
        self.ship = Ship(self.screen, self.settings)
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

    def run_game(self):
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._check_fleet_edges()
                self.aliens.update()
                self._update_bullets()
                self._update_alien_bullets()
                self._check_aliens_bottom()
                if pygame.sprite.spritecollideany(self.ship, self.aliens):
                    self._ship_hit()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.stats.game_active:
                    self._check_play_button(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_RIGHT:
                    self.ship.moving_right = True
                elif event.key == pygame.K_LEFT:
                    self.ship.moving_left = True
                elif event.key == pygame.K_SPACE and len(self.bullets) < 3:
                    self.bullets.add(Bullet(self.ship, self.settings))
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.ship.moving_right = False
                elif event.key == pygame.K_LEFT:
                    self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        if self.play_button.rect.collidepoint(mouse_pos):
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            self._create_fleet()
            self.ship.rect.midbottom = self.screen.get_rect().midbottom
            pygame.mouse.set_visible(False)

    def _ship_hit(self):
        self.stats.ships_left -= 1
        self.sb.prep_ships()
        if self.stats.ships_left == 0:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
            return
        self.aliens.empty()
        self.bullets.empty()
        self.alien_bullets.empty()
        self._create_fleet()
        self.ship.rect.midbottom = self.screen.get_rect().midbottom
        time.sleep(0.5)

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.height:
                self._ship_hit()
                break

    def _create_fleet(self):
        alien = Alien(self.screen, self.settings)
        alien_width, alien_height = alien.rect.size
        screen_rect = self.screen.get_rect()

        available_x = screen_rect.width - 2 * alien_width
        aliens_per_row = available_x // (2 * alien_width)

        available_y = screen_rect.height - 3 * alien_height - self.ship.rect.height
        number_of_rows = available_y // (2 * alien_height)

        for row in range(number_of_rows):
            for col in range(aliens_per_row):
                alien = Alien(self.screen, self.settings)
                alien.rect.x = alien_width + col * (2 * alien_width)
                alien.rect.y = alien_height + row * (2 * alien_height)
                self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                for a in self.aliens.sprites():
                    a.rect.y += self.settings.fleet_drop_speed
                self.settings.fleet_direction *= -1
                break

    def _update_alien_bullets(self):
        if (self.aliens and
                len(self.alien_bullets) < self.settings.max_alien_bullets and
                random.random() < self.settings.alien_shoot_chance):
            shooter = random.choice(self.aliens.sprites())
            self.alien_bullets.add(AlienBullet(shooter, self.settings))

        self.alien_bullets.update()

        screen_height = self.screen.get_rect().height
        for b in [b for b in self.alien_bullets if b.rect.top >= screen_height]:
            self.alien_bullets.remove(b)

        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()

    def _update_bullets(self):
        self.bullets.update()
        for bullet in [b for b in self.bullets if b.rect.bottom < 0]:
            self.bullets.remove(bullet)
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens_hit in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens_hit)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            self.bullets.empty()
            self.alien_bullets.empty()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()
            self._create_fleet()

    def _update_screen(self):
        self.screen.fill((0, 0, 0))
        for x, y in self.dots:
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 2)
        self.aliens.draw(self.screen)
        self.ship.blitme()
        self.bullets.draw(self.screen)
        self.alien_bullets.draw(self.screen)
        self.sb.show_score()
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()

if __name__ == '__main__':
    AlienInvasion().run_game()
