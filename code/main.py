import pygame, sys
from settings import *
# Move pygame.init() to the top before other imports
pygame.init()
from debug import debug
from level import Level
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cycle of Curse")
        self.clock = pygame.time.Clock()
        self.level = Level(self.screen)
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit() # <--- Clearly exit the program here
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)
if __name__ == "__main__":
    game = Game()
    game.run()