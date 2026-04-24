import pygame

class Ship(pygame.sprite.Sprite):
    def __init__(self, screen, settings):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.settings = settings
        self.moving_right = False
        self.moving_left = False

        self.image = pygame.Surface((64, 80), pygame.SRCALPHA)
        self._draw_possum()

        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom

    def _draw_possum(self):
        gray      = (180, 180, 180)
        dark_gray = (100, 100, 100)
        pink      = (255, 160, 160)
        black     = (15,  15,  15)
        white     = (245, 245, 245)

        # Tail curled at bottom
        pygame.draw.ellipse(self.image, dark_gray, (12, 66, 40, 14))
        pygame.draw.ellipse(self.image, pink,      (18, 69, 28,  8))

        # Body
        pygame.draw.ellipse(self.image, gray, (10, 38, 44, 36))

        # Head
        pygame.draw.ellipse(self.image, gray, (14, 12, 36, 30))

        # Left ear (outer + inner)
        pygame.draw.polygon(self.image, dark_gray, [(14, 22), (4,  2), (22, 14)])
        pygame.draw.polygon(self.image, pink,      [(14, 20), (8,  6), (21, 14)])

        # Right ear (outer + inner)
        pygame.draw.polygon(self.image, dark_gray, [(50, 22), (60, 2), (42, 14)])
        pygame.draw.polygon(self.image, pink,      [(50, 20), (56, 6), (43, 14)])

        # Pointed snout aimed upward
        pygame.draw.polygon(self.image, white, [(24, 22), (40, 22), (32, 2)])

        # Eyes
        pygame.draw.circle(self.image, black, (24, 26), 4)
        pygame.draw.circle(self.image, black, (40, 26), 4)
        pygame.draw.circle(self.image, white, (25, 25), 2)
        pygame.draw.circle(self.image, white, (41, 25), 2)

        # Pink nose at snout tip
        pygame.draw.circle(self.image, pink, (32, 4), 2)

    def update(self):
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.rect.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.rect.x -= self.settings.ship_speed

    def blitme(self):
        self.screen.blit(self.image, self.rect)
