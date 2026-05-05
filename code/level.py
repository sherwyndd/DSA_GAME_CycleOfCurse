import pygame 
from settings import *
from tile import Tile
from player import Player
from weapon import Weapon
from ui import UI

class Level:
	def __init__(self):

		# get the display surface 
		self.display_surface = pygame.display.get_surface()

		# sprite group setup
		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()

		# attack sprites
		self.current_attack = None

		# background setup - now handled in create_map
		# self.full_bg_surf = pygame.image.load('../image/background4.png').convert_alpha()

		# sprite setup
		self.current_map = 'main'
		self.create_map()
		
		# user interface
		self.ui = UI()

	def create_map(self):
		map_data = MAPS[self.current_map]
		layout = map_data['layout']
		self.map_width = map_data['width']
		self.map_height = map_data['height']
		
		# calculate tile sizes dynamically for current map
		self.t_width = self.map_width // COLS
		self.t_height = self.map_height // ROWS

		# update floor in camera group
		self.visible_sprites.update_floor(map_data['bg'], (self.map_width, self.map_height))

		for row_index,row in enumerate(layout):
			for col_index, col in enumerate(row):
				x = col_index * self.t_width
				y = row_index * self.t_height

				if col == 'h' or col == 'x':
					if col == 'h':
						offset = self.t_height * 0.5
						tile_surf = pygame.Surface((self.t_width, self.t_height + offset), pygame.SRCALPHA)
						tile_surf.blit(self.visible_sprites.floor_surf, (0, 0), pygame.Rect(x, y - offset, self.t_width, self.t_height + offset))
						Tile((x, y - offset), [self.visible_sprites, self.obstacle_sprites], 'object', tile_surf)
					else:
						tile_surf = pygame.Surface((self.t_width, self.t_height), pygame.SRCALPHA)
						tile_surf.blit(self.visible_sprites.floor_surf, (0, 0), pygame.Rect(x, y, self.t_width, self.t_height))
						Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'invisible', tile_surf)

				if col == 'g':
					tile_surf = pygame.Surface((self.t_width, self.t_height))
					tile_surf.fill('black')
					Tile((x, y), [self.visible_sprites], 'object', tile_surf)


				if col == 'p':
					if not hasattr(self, 'player'):
						self.player = Player((x,y),[self.visible_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack)
					else:
						self.player.hitbox.center = (x,y)
						self.player.rect.center = self.player.hitbox.center

	def switch_map(self, new_map, spawn_pos = None):
		print(f"Switching to {new_map} at {spawn_pos}")
		# clear all sprites
		for sprite in self.visible_sprites:
			if sprite != self.player: sprite.kill()
		for sprite in self.obstacle_sprites:
			sprite.kill()
		
		self.current_map = new_map
		self.create_map()
		
		if spawn_pos:
			self.player.hitbox.center = spawn_pos
			self.player.rect.center = self.player.hitbox.center

	def check_map_transition(self):
		if self.current_map == 'main':
			# Switch to second map if going right into the gate
			if self.player.hitbox.centerx > self.map_width - 40:
				self.switch_map('second', spawn_pos = (80, self.player.hitbox.centery))
		elif self.current_map == 'second':
			# Switch back to main map if going left
			if self.player.hitbox.centerx < 40:
				self.switch_map('main', spawn_pos = (self.map_width - 80, self.player.hitbox.centery))

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
		self.check_map_transition()
		self.ui.display(self.player)

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):

		# general setup 
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()
		self.floor_surf = None
		self.floor_rect = None

	def update_floor(self, path, size):
		self.floor_surf = pygame.image.load(path).convert()
		self.floor_surf = pygame.transform.scale(self.floor_surf, size)
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