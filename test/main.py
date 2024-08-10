import pygame
import sys
from start_view import start_view
from run_view import run_view

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pygame Sample")

    current_view = "start"

    while True:
        if current_view == "start":
            current_view = start_view(screen)
        elif current_view == "run":
            current_view = run_view(screen)
        elif current_view == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
