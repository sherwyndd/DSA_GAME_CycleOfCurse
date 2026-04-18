import pygame
from player import Player
from settings import *

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
        self.player = Player((WIDTH // 2, HEIGHT // 2), [self.visible_sprites])

    def run(self):
        # Update and draw the sprites
        self.visible_sprites.update()
        self.visible_sprites.draw(self.display_surface)