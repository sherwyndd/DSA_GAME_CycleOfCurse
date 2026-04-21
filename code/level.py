import pygame
from player import Player
from settings import *
from tile import Tile

class Level:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        
        # Sprite groups
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        
        # Load the full background image for auto-cropping object slices
        self.full_bg_surf = pygame.image.load('../image/background4.png').convert_alpha()
        
        # Sprite setup
        self.create_map()

    def create_map(self):
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * T_WIDTH
                y = row_index * T_HEIGHT
                
                # Logic for obstacle tiles ('x' and 'h')
                if col == 'h' or col == 'x':
                    # Determine tile dimensions and offset
                    if col == 'h':
                        # torch or taller object
                        offset = T_HEIGHT * 0.5
                        tile_surf = pygame.Surface((T_WIDTH, T_HEIGHT + offset), pygame.SRCALPHA)
                        tile_surf.blit(self.full_bg_surf, (0, 0), pygame.Rect(x, y - offset, T_WIDTH, T_HEIGHT + offset))
                        Tile((x, y - offset), [self.visible_sprites, self.obstacle_sprites], surface = tile_surf)
                    else:
                        # standard obstacle
                        tile_surf = pygame.Surface((T_WIDTH, T_HEIGHT), pygame.SRCALPHA)
                        tile_surf.blit(self.full_bg_surf, (0, 0), pygame.Rect(x, y, T_WIDTH, T_HEIGHT))
                        Tile((x, y), [self.visible_sprites, self.obstacle_sprites], surface = tile_surf)

                if col == 'p':
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)

    def run(self):
        # Update and draw the sprites
        self.visible_sprites.update()
        self.visible_sprites.custom_draw(self.player)

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # Floor setup
        self.floor_surf = pygame.image.load('../image/background4.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

    def custom_draw(self, player):
        # Getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # Camera Clamping
        if self.offset.x < 0: 
            self.offset.x = 0
        elif self.offset.x > self.floor_rect.width - (self.half_width * 2):
            self.offset.x = self.floor_rect.width - (self.half_width * 2)

        if self.offset.y < 0: 
            self.offset.y = 0
        elif self.offset.y > self.floor_rect.height - (self.half_height * 2):
            self.offset.y = self.floor_rect.height - (self.half_height * 2)

        # 1. Drawing the floor first
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # 2. Drawing sprites including player, sorted by hitbox.centery for depth effect
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.hitbox.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)