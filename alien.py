import pygame

class Alien(pygame.sprite.Sprite):
    def __init__(self, screen, settings):
        super().__init__()
        self.screen = screen
        self.settings = settings
        self.width = 40
        self.height = 30

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_eagle()
        self.rect = self.image.get_rect()
        self.rect.topleft = (50, 50)

    def _draw_eagle(self):
        steel  = (60,  80, 110)
        silver = (160, 180, 200)
        white  = (240, 240, 240)
        gold   = (255, 210,   0)
        cyan   = (0,  220, 255)
        navy   = (20,  28,  50)

        # Wings (drawn first so body overlaps the inner edges)
        pygame.draw.polygon(self.image, steel,  [(0, 10), (14, 15), (6, 25)])
        pygame.draw.polygon(self.image, steel,  [(40, 10), (26, 15), (34, 25)])
        pygame.draw.polygon(self.image, silver, [(0, 10), (14, 15), (6, 25)], 1)
        pygame.draw.polygon(self.image, silver, [(40, 10), (26, 15), (34, 25)], 1)

        # Futuristic energy lines on wings
        pygame.draw.line(self.image, cyan, (2,  12), (13, 15), 1)
        pygame.draw.line(self.image, cyan, (4,  18), (11, 21), 1)
        pygame.draw.line(self.image, cyan, (38, 12), (27, 15), 1)
        pygame.draw.line(self.image, cyan, (36, 18), (29, 21), 1)

        # Body
        pygame.draw.ellipse(self.image, navy,  (13, 13, 14, 15))
        pygame.draw.ellipse(self.image, steel, (14, 14, 12,  9))
        pygame.draw.ellipse(self.image, silver,(15, 15, 10,  6), 1)  # chest plate

        # Head (white — bald eagle reference)
        pygame.draw.circle(self.image, white, (20, 7), 6)

        # Beak points downward toward the player
        pygame.draw.polygon(self.image, gold, [(17, 11), (23, 11), (20, 15)])

        # Glowing cyan eyes
        pygame.draw.circle(self.image, cyan,  (17, 6), 2)
        pygame.draw.circle(self.image, cyan,  (23, 6), 2)
        pygame.draw.circle(self.image, white, (17, 6), 1)
        pygame.draw.circle(self.image, white, (23, 6), 1)

        # Tail feathers
        pygame.draw.polygon(self.image, steel,  [(15, 27), (20, 30), (25, 27)])
        pygame.draw.line(self.image, silver, (17, 27), (18, 30), 1)
        pygame.draw.line(self.image, silver, (23, 27), (22, 30), 1)

    def check_edges(self):
        screen_rect = self.screen.get_rect()
        return self.rect.right >= screen_rect.right or self.rect.left <= 0

    def update(self):
        self.rect.x += self.settings.alien_speed * self.settings.fleet_direction

    def draw_alien(self):
        self.screen.blit(self.image, self.rect)
