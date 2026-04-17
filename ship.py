import pygame

class Ship:
    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.image = pygame.Surface((60, 40), pygame.SRCALPHA)
        # Body
        pygame.draw.polygon(self.image, (0, 200, 255), [(30, 0), (60, 40), (0, 40)])
        # Cockpit
        pygame.draw.polygon(self.image, (255, 255, 255), [(30, 8), (42, 34), (18, 34)])

        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom

    def blitme(self):
        self.screen.blit(self.image, self.rect)
