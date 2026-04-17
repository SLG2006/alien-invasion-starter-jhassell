import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, ship):
        super().__init__()
        self.speed = 10

        self.image = pygame.Surface((4, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (180, 0,   0),   (0, 0, 4, 20))  # outer beam
        pygame.draw.rect(self.image, (255, 80,  80),  (1, 0, 2, 20))  # bright core
        pygame.draw.rect(self.image, (255, 220, 220), (1, 0, 2,  5))  # hot tip

        self.rect = self.image.get_rect()
        self.rect.midbottom = ship.rect.midtop

    def update(self):
        self.rect.y -= self.speed
