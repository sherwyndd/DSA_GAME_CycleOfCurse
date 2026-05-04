import pygame, sys
from settings import *
# Move pygame.init() to the top before other imports
pygame.init()
from debug import debug
from level import Level
class Game:
    """
    Lớp khởi tạo chính của trò chơi.
    Thiết lập cửa sổ, vòng lặp game (game loop) và quản lý tiến trình chung của ứng dụng.
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cycle of Curse")
        self.clock = pygame.time.Clock()
        self.level = Level(self.screen)
        
    def run(self):
        """
        Vòng lặp chính của trò chơi.
        Xử lý các sự kiện, cập nhật logic và vẽ lại khung hình (60 FPS).
        """
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