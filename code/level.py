import pygame 
from settings import *
from tile import Tile
from player import Player
from weapon import Weapon

class Level:
	def __init__(self):

		# get the display surface 
		self.display_surface = pygame.display.get_surface()

		# sprite group setup
		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()

		# attack sprites
		self.current_attack = None

		# background setup
		self.full_bg_surf = pygame.image.load('../image/background4.png').convert_alpha()

		# sprite setup
		self.create_map()

	def create_map(self):
		for row_index,row in enumerate(WORLD_MAP):
			for col_index, col in enumerate(row):
				x = col_index * T_WIDTH
				y = row_index * T_HEIGHT

				if col == 'h' or col == 'x':
					if col == 'h':
						offset = T_HEIGHT * 0.5
						tile_surf = pygame.Surface((T_WIDTH, T_HEIGHT + offset), pygame.SRCALPHA)
						tile_surf.blit(self.full_bg_surf, (0, 0), pygame.Rect(x, y - offset, T_WIDTH, T_HEIGHT + offset))
						Tile((x, y - offset), [self.visible_sprites, self.obstacle_sprites], 'object', tile_surf)
					else:
						tile_surf = pygame.Surface((T_WIDTH, T_HEIGHT), pygame.SRCALPHA)
						tile_surf.blit(self.full_bg_surf, (0, 0), pygame.Rect(x, y, T_WIDTH, T_HEIGHT))
						Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'invisible', tile_surf)


				if col == 'p':
					self.player = Player((x,y),[self.visible_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack)

	def create_attack(self):
		self.current_attack = Weapon(self.player,[self.visible_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def run(self):
		# update and draw the game
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update()

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):

		# general setup 
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()

		# creating the floor
		self.floor_surf = pygame.image.load('../image/background4.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self,player):

		# getting the offset 
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		# camera clamping
		if self.offset.x < 0: self.offset.x = 0
		elif self.offset.x > self.floor_rect.width - (self.half_width * 2):
			self.offset.x = self.floor_rect.width - (self.half_width * 2)

		if self.offset.y < 0: self.offset.y = 0
		elif self.offset.y > self.floor_rect.height - (self.half_height * 2):
			self.offset.y = self.floor_rect.height - (self.half_height * 2)

		# drawing the floor
		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf,floor_offset_pos)

		# sorting sprites for depth effect
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.hitbox.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)