import pygame

class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, alien, settings):
        super().__init__()
        self.speed = settings.alien_bullet_speed

        self.image = pygame.Surface((5, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (140,   0, 200), (0,  0, 5, 16))  # outer beam
        pygame.draw.rect(self.image, (220,  80, 255), (1,  0, 3, 16))  # bright core
        pygame.draw.rect(self.image, (255, 200, 255), (1, 11, 3,  5))  # hot tip at bottom

        self.rect = self.image.get_rect()
        self.rect.midtop = alien.rect.midbottom

    def update(self):
        self.rect.y += self.speed
