import pygame
import random
from ship import Ship
from bullet import Bullet

class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Alien Invasion")
        self.clock = pygame.time.Clock()
        self.dots = [(random.randint(0, 800), random.randint(0, 600)) for _ in range(150)]
        self.ship = Ship(self.screen)
        self.bullets = pygame.sprite.Group()

    def run_game(self):
        while True:
            self._check_events()
            self.ship.update()
            self._update_bullets()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.ship.moving_right = True
                elif event.key == pygame.K_LEFT:
                    self.ship.moving_left = True
                elif event.key == pygame.K_SPACE and len(self.bullets) < 3:
                    self.bullets.add(Bullet(self.ship))
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.ship.moving_right = False
                elif event.key == pygame.K_LEFT:
                    self.ship.moving_left = False

    def _update_bullets(self):
        self.bullets.update()
        for bullet in [b for b in self.bullets if b.rect.bottom < 0]:
            self.bullets.remove(bullet)

    def _update_screen(self):
        self.screen.fill((0, 0, 0))
        for x, y in self.dots:
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 2)
        self.ship.blitme()
        self.bullets.draw(self.screen)
        pygame.display.flip()

if __name__ == '__main__':
    AlienInvasion().run_game()
