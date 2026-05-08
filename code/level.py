import pygame 
import random
from settings import *
from tile import Tile
from player import Player
from enemy import Enemy
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
		self.attack_sprites = pygame.sprite.Group()
		self.enemy_attack_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()

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

		# monster tracking
		self.total_monsters = 0
		self.current_monsters = 0

		# gate management
		self.gate_sprites = pygame.sprite.Group()
		self.entrance_gates = pygame.sprite.Group()

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

		# reset counts and groups
		self.total_monsters = 0
		self.gate_sprites.empty()
		self.entrance_gates.empty()

		for row_index,row in enumerate(layout):
			for col_index, col in enumerate(row):
				x = col_index * self.t_width
				y = row_index * self.t_height

				if (row_index, col_index) in map_data.get('gates', []):
					# This is a gate position
					# 1. 'Open' state: Copy floor from neighbor
					neighbor_col = col_index - 1 if col_index > 0 else col_index + 1
					neighbor_x = neighbor_col * self.t_width
					open_surf = pygame.Surface((self.t_width, self.t_height))
					open_surf.blit(self.visible_sprites.floor_surf, (0, 0), pygame.Rect(neighbor_x, y, self.t_width, self.t_height))
					open_surf = pygame.transform.flip(open_surf, True, False)
					
					# 2. 'Closed' state: Use original background at this position
					closed_surf = pygame.Surface((self.t_width, self.t_height))
					closed_surf.blit(self.visible_sprites.floor_surf, (0, 0), pygame.Rect(x, y, self.t_width, self.t_height))
					
					# Create the gate tile (collision only, not in visible_sprites)
					gate_tile = Tile((x, y), [self.obstacle_sprites, self.gate_sprites], 'gate', closed_surf)
					gate_tile.closed_surf = closed_surf
					gate_tile.open_surf = open_surf
					continue

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

				if col == 'p':
					if not hasattr(self, 'player'):
						self.player = Player((x,y),[self.visible_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack)
						self.player.create_magic = self.create_magic
					else:
						self.player.hitbox.center = (x,y)
						self.player.rect.center = self.player.hitbox.center

		# Spawn spirits randomly
		empty_tiles = []
		for row_index, row in enumerate(layout):
			for col_index, col in enumerate(row):
				if col == ' ':
					x = col_index * self.t_width
					y = row_index * self.t_height
					empty_tiles.append((x, y))
		
		if empty_tiles:
			spawn_count = min(5, len(empty_tiles))
			self.total_monsters = spawn_count
			for pos in random.sample(empty_tiles, spawn_count):
				Enemy('spirit', pos, [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.damage_player)
		else:
			self.total_monsters = 0

		# Spawn boss on first map
		if self.current_map == 'first':
			Enemy('boss', (self.map_width // 2, self.map_height // 2), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.damage_player, self.create_enemy_attack, self.destroy_enemy_attack)
			self.total_monsters += 1

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
			
			# Identify and close entrance gates permanently
			for gate in self.gate_sprites:
				# If gate is close to the spawn position horizontally, it's an entrance
				if abs(gate.rect.centerx - spawn_pos[0]) < 200:
					self.entrance_gates.add(gate)
					self.gate_sprites.remove(gate)
					# Keep the original background (fence) visual on the floor
					self.visible_sprites.floor_surf.blit(gate.closed_surf, gate.rect.topleft)
					# Keep it in obstacle_sprites forever

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
		self.current_attack = Weapon(self.player,[self.visible_sprites, self.attack_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def create_magic(self,style,strength,cost):
		if style == 'heal':
			self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])

	def create_enemy_attack(self, enemy):
		Weapon(enemy, [self.visible_sprites, self.enemy_attack_sprites])

	def destroy_enemy_attack(self, enemy):
		for sprite in self.enemy_attack_sprites:
			sprite.kill()

	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						target_sprite.get_damage(self.player,attack_sprite.sprite_type)

	def enemy_attack_logic(self):
		if self.enemy_attack_sprites:
			for attack_sprite in self.enemy_attack_sprites:
				if attack_sprite.rect.colliderect(self.player.hitbox):
					self.damage_player(attack_sprite.owner.attack_damage, 'weapon')
					# To prevent multiple hits per attack, we rely on player's invincibility duration

	def damage_player(self,amount,attack_type):
		if self.player.vulnerable:
			actual_damage = amount - self.player.armor
			if actual_damage < 0: actual_damage = 0
			
			self.player.health -= actual_damage
			self.player.target_health -= actual_damage
			if self.player.health < 0: self.player.health = 0
			if self.player.target_health < 0: self.player.target_health = 0
			
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			# spawn particles or play sounds here

	def update_gate_state(self):
		self.current_monsters = len(self.attackable_sprites)
		
		# Regular gates (not entrance gates)
		for gate in self.gate_sprites:
			if self.current_monsters == 0:
				# Win condition: show "open" floor and make it passable
				if gate in self.obstacle_sprites:
					self.obstacle_sprites.remove(gate)
					# Update floor visual
					self.visible_sprites.floor_surf.blit(gate.open_surf, gate.rect.topleft)
			else:
				# Still have monsters: show original background (fence) and block
				if gate not in self.obstacle_sprites:
					self.obstacle_sprites.add(gate)
					# Restore floor visual
					self.visible_sprites.floor_surf.blit(gate.closed_surf, gate.rect.topleft)

	def run(self):
		# update and draw the game
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update()
		self.visible_sprites.enemy_update(self.player)
		self.player_attack_logic()
		self.enemy_attack_logic()
		self.update_gate_state()
		self.check_map_transition()
		self.ui.display(self.player, MAPS[self.current_map]['index'], self.current_monsters, self.total_monsters)

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

	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)