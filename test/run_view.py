import pygame
import random

def run_view(screen):
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        screen.fill((255, 255, 255))

        for _ in range(100):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            screen.set_at((x, y), (0, 0, 0))

        pygame.display.flip()
        clock.tick(60)
