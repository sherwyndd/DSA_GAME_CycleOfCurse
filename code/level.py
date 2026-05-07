import pygame 
from settings import *
from tile import Tile
from player import Player
from weapon import Weapon
from ui import UI
from magic import MagicPlayer
from support import remove_background_floodfill

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
		# self.full_bg_surf = pygame.image.load('../graphics/background4.png').convert_alpha()

		# sprite setup
		self.current_map = 'first'
		
		# background cache
		self.bg_cache = {}
		for map_name, data in MAPS.items():
			path = data['bg']
			size = (data['width'], data['height'])
			surf = pygame.image.load(path).convert()
			surf = pygame.transform.scale(surf, size)
			self.bg_cache[map_name] = surf

		self.create_map()
		
		# user interface
		self.ui = UI()

		# magic 
		self.magic_player = MagicPlayer(None)

	def create_map(self):
		map_data = MAPS[self.current_map]
		layout = map_data['layout']
		self.map_width = map_data['width']
		self.map_height = map_data['height']
		
		# calculate tile sizes dynamically for current map
		self.t_width = self.map_width // COLS
		self.t_height = self.map_height // ROWS

		# update floor in camera group
		self.visible_sprites.update_floor_from_surf(self.bg_cache[self.current_map])

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
					# Determine neighbor for seamless transition
					neighbor_col = col_index - 1 if col_index > 0 else col_index + 1
					neighbor_x = neighbor_col * self.t_width
					
					# Copy floor from neighbor, flip it, and blit onto current floor
					gate_surf = pygame.Surface((self.t_width, self.t_height))
					gate_surf.blit(self.visible_sprites.floor_surf, (0, 0), pygame.Rect(neighbor_x, y, self.t_width, self.t_height))
					gate_surf = pygame.transform.flip(gate_surf, True, False)
					
					self.visible_sprites.floor_surf.blit(gate_surf, (x, y))
					
					# No longer adding to obstacle_sprites so player can walk through to transition
					Tile((x, y), [], 'invisible', pygame.Surface((self.t_width, self.t_height), pygame.SRCALPHA))


				if col == 'p':
					if not hasattr(self, 'player'):
						self.player = Player((x,y),[self.visible_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack)
						self.player.create_magic = self.create_magic
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
		if self.current_map == 'first':
			# Map 1 -> Map 2 (Right)
			if self.player.hitbox.centerx > self.map_width - 40:
				self.switch_map('second', spawn_pos = (80, self.player.hitbox.centery))
		elif self.current_map == 'second':
			# Map 2 -> Map 1 (Left)
			if self.player.hitbox.centerx < 40:
				self.switch_map('first', spawn_pos = (self.map_width - 80, self.player.hitbox.centery))
			# Map 2 -> Map 3 (Right)
			elif self.player.hitbox.centerx > self.map_width - 40:
				self.switch_map('third', spawn_pos = (80, self.player.hitbox.centery))
		elif self.current_map == 'third':
			# Map 3 -> Map 2 (Left)
			if self.player.hitbox.centerx < 40:
				self.switch_map('second', spawn_pos = (self.map_width - 80, self.player.hitbox.centery))
			# Map 3 -> Map 4 (Right)
			elif self.player.hitbox.centerx > self.map_width - 40:
				self.switch_map('fourth', spawn_pos = (80, self.player.hitbox.centery))
		elif self.current_map == 'fourth':
			# Map 4 -> Map 3 (Left)
			if self.player.hitbox.centerx < 40:
				self.switch_map('third', spawn_pos = (self.map_width - 80, self.player.hitbox.centery))

	def create_attack(self):
		self.current_attack = Weapon(self.player,[self.visible_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def create_magic(self,style,strength,cost):
		if style == 'heal':
			self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])

	def run(self):
		# update and draw the game
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update()
		self.check_map_transition()
		self.ui.display(self.player, MAPS[self.current_map]['index'])

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

	def update_floor_from_surf(self, surf):
		self.floor_surf = surf.copy()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

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
			# draw ghosts for player
			if hasattr(sprite, 'draw_ghosts'):
				sprite.draw_ghosts(self.display_surface, self.offset)

			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)