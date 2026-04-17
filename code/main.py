import pygame, sys
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DSA Game")
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load("../image/background.png")
    def run(self):
        while True:
            self.screen.blit(self.background, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            self.clock.tick(FPS)
if __name__ == "__main__":
    game = Game()
    game.run()