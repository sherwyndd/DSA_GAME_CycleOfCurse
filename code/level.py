import pygame
from player import Player
from settings import *
from tile import Tile
class Level:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        
        # Sprite groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        
        # Sprite setup
        self.create_map()

    def create_map(self):
        # Start the player in the middle of the screen
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * T_WIDTH
                y = row_index * T_HEIGHT
                if (col == 'h'):
                    y = row_index * 1.07 * T_HEIGHT
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                if col == 'x':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                if col == 'p':
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)

    def run(self):
        # Update and draw the sprites
        self.visible_sprites.update()
        self.visible_sprites.draw(self.display_surface)