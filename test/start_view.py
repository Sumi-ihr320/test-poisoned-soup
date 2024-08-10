import pygame
import sys

def start_view(screen):
    start_button = pygame.Rect(350, 250, 100, 50)
    font = pygame.font.Font(None, 36)
    button_text = font.render("Start", True, (255, 255, 255))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "run"

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 0, 0), start_button)
        screen.blit(button_text, (start_button.x + 10, start_button.y + 10))
        pygame.display.flip()
