import pygame, sys
from settings import *
from level import Level
from menu import Menu, Leaderboard

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Cycle of Curse')
        self.clock = pygame.time.Clock()

        self.state = 'MENU'
        self.menu = Menu()
        self.leaderboard = Leaderboard()
        self.level = None
        self.record_saved = False

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Menu Input handling
                if self.state == 'MENU':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w or event.key == pygame.K_UP:
                            self.menu.selection_index = (self.menu.selection_index - 1) % len(self.menu.buttons)
                        elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                            self.menu.selection_index = (self.menu.selection_index + 1) % len(self.menu.buttons)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            selection = self.menu.buttons[self.menu.selection_index]
                            if selection == 'PLAY GAME':
                                self.level = Level()
                                self.state = 'GAME'
                                self.record_saved = False
                            elif selection == 'LEADERBOARD':
                                self.state = 'LEADERBOARD'
                            elif selection == 'EXIT':
                                pygame.quit()
                                sys.exit()
                
                elif self.state == 'LEADERBOARD':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = 'MENU'

            if self.state == 'MENU':
                self.menu.display()
            elif self.state == 'LEADERBOARD':
                self.leaderboard.display()
            elif self.state == 'GAME':
                self.screen.fill('black')
                self.level.run(events)
                
                # Check for game state changes from Level
                if self.level.status == 'game_over' and not self.record_saved:
                    # Save progress: Round index and time
                    round_idx = MAPS[self.level.current_map]['index']
                    elapsed_time = (pygame.time.get_ticks() - self.level.start_time) // 1000
                    self.leaderboard.save_record(f'Round {round_idx}', elapsed_time)
                    self.record_saved = True
                
                elif self.level.status == 'win' and not self.record_saved:
                    elapsed_time = (pygame.time.get_ticks() - self.level.start_time) // 1000
                    self.leaderboard.save_record('Win', elapsed_time)
                    self.record_saved = True
                
                elif self.level.status == 'back_to_menu':
                    self.state = 'MENU'
                    self.level = None

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()