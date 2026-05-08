import pygame


class Beam(pygame.sprite.Sprite):
    damage = 5

    def __init__(self, ship):
        super().__init__()
        beam_width = 20
        beam_height = max(ship.rect.top, 1)

        self.image = pygame.Surface((beam_width, beam_height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0,  80,   0),  (0, 0, beam_width, beam_height))
        pygame.draw.rect(self.image, (0, 200,   0),  (4, 0, 12,         beam_height))
        pygame.draw.rect(self.image, (150, 255, 150), (8, 0,  4,         beam_height))

        self.rect = self.image.get_rect()
        self.rect.midbottom = ship.rect.midtop
        self.lifetime = 15

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
