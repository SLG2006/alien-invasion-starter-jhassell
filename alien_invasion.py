import pygame
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
DOT_COUNT = 150

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Alien Invasion")
clock = pygame.time.Clock()

dots = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(DOT_COUNT)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    for x, y in dots:
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
