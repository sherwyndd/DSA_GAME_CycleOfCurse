"""
Level Module
------------
Handles the orchestration of the game world, including map loading, sprite groups, 
collision logic, and game state transitions.

DSA Integration:
- YSortCameraGroup: Uses a custom sorting algorithm (Y-Sort) to manage sprite 
  layering based on vertical position, simulating 3D depth.
- Attackable Sprites: Managed through pygame groups to optimize collision 
  checks between the player, enemies, and summons.
- Map Transitions: Logic for switching between layouts and resetting world state.
"""
import pygame 
import random
from settings import *
from tile import Tile
from player import Player
from enemy import Enemy
from weapon import Weapon
from ui import UI
from magic import MagicPlayer
from particles import AnimationPlayer
from support import remove_background_floodfill

class Level:
	"""
	Lớp điều phối toàn bộ thế giới game trong một phiên chơi.

	Quản lý sprite groups, bản đồ hiện tại, trạng thái game (playing, game_over, win),
	va chạm và logic phần thưởng sau màn.

	DSA Highlights:
	- YSortCameraGroup: Sắp xếp sprite theo trục Y (Sorting) để mô phỏng chiều sâu.
	- Spatial Grid: Quản lý vị trí các thực thể để tối ưu va chạm và pathfinding.
	"""

	def __init__(self):
		"""
		Khởi tạo các thành phần cốt lõi của màn chơi:
		- Sprite groups (visible, obstacle, attackable).
		- Caching ảnh nền các map.
		- Khởi tạo UI, Timer, và các hệ thống hỗ trợ (AnimationPlayer, MagicPlayer).
		"""


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
		self.telegraphs = []
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

		# user interface
		self.ui = UI()
		now = pygame.time.get_ticks()
		self.start_time = now
		self.round_start_time = now  # HUD + leaderboard: time since current map/round began
		self.intro_sequence = []
		self.intro_started_at = 0
		self.intro_active = False
		self.intro_input_lock_until = 0

		# Leaderboard: snapshot at death/win; flushed when player picks Play Again / Back to Menu
		self.pending_leaderboard = None
		self._leaderboard_save_pending = None

		# magic 
		self.magic_player = MagicPlayer(None)

		# particles
		self.animation_player = AnimationPlayer()
		
		# skill tree / pause overlay
		self.show_skill_tree = False
		self.skill_tree_pause_start = 0
		self.pause_offset = 0
		self.skill_tree_category_index = 0
		self.skill_tree_skill_index = 0
		self.skill_tree_mode = 'category'
		self.skill_tree_scroll = 0
		
		# Game over / Win
		self.game_over_selection = 0
		self.win_selection = 0
		self.status = 'playing'
		self.enemy_intro_text = {
			'spirit': 'A floating curse that only deals basic damage.',
			'slime': 'A jelly-like curse with basic contact damage.',
			'skeleton': 'A fragile melee bone warrior.',
			'skeleton-big': 'Heavy bruiser with stronger melee hits.',
			'skeleton-shaman': 'A caster that fires flames from range.',
			'boss': 'Close-range BOSS with axe strikes that can freeze you.',
			'boss2': 'Summoner BOSS: frogs can slow, bull charges for heavy knockback.',
			'boss3': 'Aggressive BOSS with triple-slash lance pressure.'
		}

		self.create_map()
		self.enqueue_round_intro(show_starter_weapon = True)

	def create_map(self):
		"""
		Nạp dữ liệu bản đồ từ settings.MAPS và khởi tạo các Sprite:
		- Duyệt ma trận layout: 'x' (tường), 'p' (player), 'h' (hazard), 'g' (gate).
		- Tính toán camera constraints dựa trên kích thước map.
		- Khởi tạo boss/quái vật tương ứng với từng map.
		"""

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
						self.player = Player((x,y),[self.visible_sprites, self.obstacle_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack)
						self.player.create_magic = self.create_magic
					else:
						self.player.hitbox.center = (x,y)
						self.player.rect.center = self.player.hitbox.center

		# Ensure player is created even if 'p' isn't on the map (like in map 2)
		if not hasattr(self, 'player'):
			spawn_x = self.t_width * 2
			spawn_y = self.map_height // 2
			self.player = Player((spawn_x, spawn_y),[self.visible_sprites, self.obstacle_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack)
			self.player.create_magic = self.create_magic

		# Spawn spirits randomly
		empty_tiles = []
		for row_index, row in enumerate(layout):
			for col_index, col in enumerate(row):
				if col == ' ':
					# Ensure the tile is surrounded by empty spaces so the enemy hitbox doesn't clip into walls
					safe = True
					for dr in [-1, 0, 1]:
						for dc in [-1, 0, 1]:
							r = row_index + dr
							c = col_index + dc
							if 0 <= r < len(layout) and 0 <= c < len(layout[0]):
								if layout[r][c] not in [' ', 'h']:
									safe = False
					if safe:
						x = col_index * self.t_width + self.t_width // 2
						y = row_index * self.t_height + self.t_height // 2
						empty_tiles.append((x, y))
		
		if empty_tiles and self.current_map == 'first':
			spawn_count = min(10, len(empty_tiles))
			self.total_monsters = spawn_count
			positions = random.sample(empty_tiles, spawn_count)
			for i, pos in enumerate(positions):
				if i < 5:
					Enemy('slime', pos, [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], self.obstacle_sprites, self.damage_player, self.trigger_death_particles, animation_player=self.animation_player, particle_groups=[self.visible_sprites], level=self)
				else:
					Enemy('spirit', pos, [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], self.obstacle_sprites, self.damage_player, self.trigger_death_particles, animation_player=self.animation_player, particle_groups=[self.visible_sprites], level=self)
		elif empty_tiles and self.current_map == 'fourth':
			spawn_count = min(9, len(empty_tiles))
			self.total_monsters = spawn_count
			positions = random.sample(empty_tiles, spawn_count)
			for i, pos in enumerate(positions):
				if i < 5:
					Enemy('skeleton', pos, [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], self.obstacle_sprites, self.damage_player, self.trigger_death_particles, animation_player=self.animation_player, particle_groups=[self.visible_sprites], level=self)
				elif i < 7:
					Enemy('skeleton-big', pos, [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], self.obstacle_sprites, self.damage_player, self.trigger_death_particles, animation_player=self.animation_player, particle_groups=[self.visible_sprites], level=self)
				else:
					Enemy('skeleton-shaman', pos, [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], self.obstacle_sprites, self.damage_player, self.trigger_death_particles, animation_player=self.animation_player, particle_groups=[self.visible_sprites], level=self)
		else:
			self.total_monsters = 0

		# Spawn boss on first map
		if self.current_map == 'first':
			Enemy('boss', (self.map_width // 2, self.map_height // 2), [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], self.obstacle_sprites, self.damage_player, self.trigger_death_particles, self.create_enemy_attack, self.destroy_enemy_attack, animation_player=self.animation_player, particle_groups=[self.visible_sprites], level=self)
			self.total_monsters += 1

		# Spawn boss2 on second map
		if self.current_map == 'second':
			boss2 = Enemy('boss2', (self.map_width // 2, self.map_height // 2), [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], self.obstacle_sprites, self.damage_player, self.trigger_death_particles, self.create_enemy_attack, self.destroy_enemy_attack, animation_player=self.animation_player, particle_groups=[self.visible_sprites], level=self)
			self.total_monsters += 1
			# Still need to wire summon references for logic
			self._pending_boss2 = boss2

		# Spawn boss3 (Sukuna) on fourth map
		if self.current_map == 'fourth':
			Enemy('boss3', (self.map_width // 2, self.map_height // 2), [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], self.obstacle_sprites, self.damage_player, self.trigger_death_particles, self.create_enemy_attack, self.destroy_enemy_attack, self.create_enemy_projectile, animation_player=self.animation_player, particle_groups=[self.visible_sprites], level=self)
			self.total_monsters += 1

		if self.total_monsters > 0:
			self.reward_given = False
		else:
			self.reward_given = True

	def switch_map(self, new_map, spawn_pos = None):
		print(f"Switching to {new_map} at {spawn_pos}")
		# clear all sprites
		for sprite in self.visible_sprites:
			if sprite != self.player: sprite.kill()
		for sprite in self.obstacle_sprites:
			if sprite != self.player: sprite.kill()
		
		self.current_map = new_map
		self.create_map()
		self.round_start_time = pygame.time.get_ticks()
		self.enqueue_round_intro(show_starter_weapon = False)
		self.player.health = self.player.stats['health']
		self.player.target_health = self.player.health
		self.player.potions_left = self.player.max_potions
		
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
				self.switch_map('fourth', spawn_pos = (80, self.player.hitbox.centery))
		elif self.current_map == 'fourth':
			# Map 3 -> Map 2 (Left)
			if self.player.hitbox.centerx < 40:
				self.switch_map('second', spawn_pos = (self.map_width - 80, self.player.hitbox.centery))

	def create_attack(self):
		self.current_attack = Weapon(self.player,[self.visible_sprites, self.attack_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def create_magic(self,style,strength,cost):
		if style == 'heal':
			self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])
		elif style == 'dismantle':
			self.magic_player.dismantle(self.player, [self.visible_sprites, self.attack_sprites], self.obstacle_sprites)

	def create_enemy_attack(self, enemy):
		Weapon(enemy, [self.visible_sprites, self.enemy_attack_sprites])

	def destroy_enemy_attack(self, enemy):
		for sprite in self.enemy_attack_sprites:
			sprite.kill()

	def destroy_enemy_attack(self, enemy):
		for sprite in self.enemy_attack_sprites:
			if hasattr(sprite, 'owner') and sprite.owner == enemy:
				# Don't kill projectiles/magic, let them finish their own duration
				if getattr(sprite, 'sprite_type', '') != 'magic':
					sprite.kill()

	def create_enemy_projectile(self, enemy, style, direction):
		if style == 'dismantle':
			from magic import SukunaSlash
			SukunaSlash(enemy.rect.center, direction, [self.visible_sprites, self.enemy_attack_sprites], self.obstacle_sprites, self.animation_player, self.player, owner = enemy)

	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if getattr(target_sprite, 'sprite_type', '') == 'player_summon':
							continue
						target_sprite.get_damage(self.player,attack_sprite.sprite_type)
						if hasattr(target_sprite, 'health') and target_sprite.health <= 0 and not getattr(target_sprite, 'exp_awarded', False):
							exp_gain = getattr(target_sprite, 'exp_reward', 0)
							if exp_gain:
								self.player.exp += exp_gain
							target_sprite.exp_awarded = True

	def enemy_attack_logic(self):
		if self.enemy_attack_sprites:
			for attack_sprite in self.enemy_attack_sprites:
				collision_rect = attack_sprite.hitbox if hasattr(attack_sprite, 'hitbox') else attack_sprite.rect
				
				# 1. Hit Player?
				if collision_rect.colliderect(self.player.hitbox):
					if hasattr(attack_sprite, 'owner') and attack_sprite.owner:
						weapon_type = attack_sprite.owner.weapon if hasattr(attack_sprite.owner, 'weapon') else 'weapon'
						self.damage_player(attack_sprite.owner.attack_damage, weapon_type)
						if getattr(attack_sprite, 'sprite_type', '') == 'magic':
							attack_sprite.kill()
					elif hasattr(attack_sprite, 'damage'):
						self.damage_player(attack_sprite.damage, 'weapon')
						if getattr(attack_sprite, 'sprite_type', '') == 'magic':
							attack_sprite.kill()
				
				# 2. Hit Player Summons? (Always check)
				for summon in self.visible_sprites:
					if getattr(summon, 'sprite_type', '') == 'player_summon' and summon.alive():
						if collision_rect.colliderect(summon.hitbox):
							if hasattr(attack_sprite, 'owner') and attack_sprite.owner:
								if hasattr(summon, 'get_damage'):
									# Pass the actual attacker (boss/enemy) instead of dummy player
									summon.get_damage(attack_sprite.owner, 'enemy') 
								if getattr(attack_sprite, 'sprite_type', '') == 'magic':
									attack_sprite.kill()
							elif hasattr(attack_sprite, 'damage'):
								if hasattr(summon, 'get_damage'):
									summon.get_damage(attack_sprite, 'enemy')
								if getattr(attack_sprite, 'sprite_type', '') == 'magic':
									attack_sprite.kill()

	def handle_skill_tree_input(self, events):
		categories = self.player.skill_tree_categories
		current_category = categories[self.skill_tree_category_index]
		
		# Filter nodes: 
		# 1. Weapon check
		# 2. Prerequisites check (hide LV2 until LV1 is unlocked)
		skills = [
			n for n in current_category['nodes'] 
			if (n.get('weapon') is None or n.get('weapon') in self.player.unlocked_weapons) and
			   (all(self.player.is_skill_unlocked(p) for p in n['prereq']))
		]
		
		for event in events:
			if event.type == pygame.KEYDOWN:
				if self.skill_tree_mode == 'category':
					if event.key in (pygame.K_RIGHT, pygame.K_d):
						self.skill_tree_category_index = min(self.skill_tree_category_index + 1, len(categories) - 1)
						self.skill_tree_scroll = 0
					elif event.key in (pygame.K_LEFT, pygame.K_a):
						self.skill_tree_category_index = max(self.skill_tree_category_index - 1, 0)
						self.skill_tree_scroll = 0
					elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RETURN, pygame.K_SPACE):
						if skills:
							self.skill_tree_mode = 'skill'
							self.skill_tree_skill_index = 0
							self.skill_tree_scroll = 0
				
				elif self.skill_tree_mode == 'skill':
					cols = 2
					if event.key in (pygame.K_RIGHT, pygame.K_d):
						self.skill_tree_skill_index = min(self.skill_tree_skill_index + 1, len(skills) - 1)
					elif event.key in (pygame.K_LEFT, pygame.K_a):
						self.skill_tree_skill_index = max(self.skill_tree_skill_index - 1, 0)
					elif event.key in (pygame.K_DOWN, pygame.K_s):
						max_row = (len(skills) - 1) // cols
						current_row = self.skill_tree_skill_index // cols
						if current_row == max_row:
							self.skill_tree_mode = 'category'
						else:
							self.skill_tree_skill_index = min(self.skill_tree_skill_index + cols, len(skills) - 1)
					elif event.key in (pygame.K_UP, pygame.K_w):
						current_row = self.skill_tree_skill_index // cols
						if current_row == 0:
							self.skill_tree_mode = 'category'
						else:
							self.skill_tree_skill_index = max(self.skill_tree_skill_index - cols, 0)
					elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
						if skills:
							node = skills[self.skill_tree_skill_index]
							self.player.unlock_skill(node['id'])

	def damage_player(self,amount,attack_type):
		if self.player.vulnerable:
			if attack_type == 'flame':
				# Capture position at start of warning
				pos = self.player.rect.center
				
				# 1. WARNING PHASE (0.5s): Frames 11 -> 08 (small fire)
				self.animation_player.create_particles('flame_warning', pos, [self.visible_sprites])
				
				def eruption_logic(p_pos, p_amount):
					# 2. ERUPTION PHASE (0.7s): Frames 07 -> 00 (big fire)
					# TRIGGER DAMAGE AND BURN NOW
					dist = pygame.math.Vector2(self.player.rect.center).distance_to(p_pos)
					if dist < 65:
						self.apply_flame_damage(p_amount)
						# Trigger red flicker only on initial hit
						self.player.red_flicker = True
						self.player.red_flicker_start_time = pygame.time.get_ticks()

					self.animation_player.create_particles('flame_erupt', p_pos, [self.visible_sprites])

				# Schedule eruption after 500ms warning
				self.telegraphs.append({'time': pygame.time.get_ticks() + 500, 'callback': eruption_logic, 'args': (pos, amount)})
				return

			actual_damage = amount - self.player.armor
			if actual_damage < 0: actual_damage = 0
			
			from player import GOD_MODE
			if not GOD_MODE:
				self.player.target_health -= actual_damage
				if self.player.target_health < 0: self.player.target_health = 0
				# self.player.health stays the same, will catch up in update()
			
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			self.player.hit_flash = True
			self.player.hit_flash_time = pygame.time.get_ticks()

			if attack_type == 'axe':
				if random.random() < 0.4:
					frozen_pos = (self.player.rect.midbottom[0], self.player.rect.midbottom[1] + 20)
					self.animation_player.create_particles('frozen', frozen_pos, [self.visible_sprites], pos_type='midbottom')
					self.player.freeze()
			elif attack_type == 'bull':
				# Knockback 20px away from the SOURCE of damage (any Bull)
				bulls = [s for s in self.visible_sprites if hasattr(s, 'variant') and s.variant == 'bull']
				if bulls:
					nearest_bull = sorted(bulls, key=lambda s: pygame.math.Vector2(s.rect.center).distance_to(self.player.rect.center))[0]
					diff = (pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(nearest_bull.rect.center))
					if diff.magnitude() > 0:
						self.player.knockback_vector = diff.normalize() * 20
					else:
						self.player.knockback_vector = pygame.math.Vector2(0, 20)
				else:
					self.player.knockback_vector = pygame.math.Vector2(0, 20)
				
				self.player.knockback_time = pygame.time.get_ticks()
			elif attack_type == 'frog':
				self.player.is_slowed = True
				self.player.slow_start_time = pygame.time.get_ticks()
			elif attack_type == 'lance':
				# Triple slash: center + above + below
				cx, cy = self.player.rect.center
				self.animation_player.create_particles('lance', (cx, cy), [self.visible_sprites])
				self.animation_player.create_particles('lance_small', (cx, cy - 25), [self.visible_sprites])
				self.animation_player.create_particles('lance_small', (cx, cy + 25), [self.visible_sprites])
			elif attack_type != 'none':
				self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

	def apply_flame_damage(self, amount):
		dmg = amount - self.player.armor
		if dmg < 1: dmg = 1
		
		from player import GOD_MODE
		if not GOD_MODE:
			self.player.target_health -= dmg
			if self.player.target_health < 0: self.player.target_health = 0
			
		self.player.is_burning = True
		self.player.burn_start_time = pygame.time.get_ticks()
		self.player.last_burn_damage_time = self.player.burn_start_time
		self.player.hit_flash = True
		self.player.hit_flash_time = pygame.time.get_ticks()

	def trigger_death_particles(self, pos, particle_type):
		self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])

	def update_gate_state(self):
		"""
		Kiểm tra điều kiện mở cổng (Win Condition):
		- Đếm số lượng quái vật hiện tại (loại bỏ player_summon).
		- Nếu quái = 0: Mở các cổng chắn bằng cách xóa khỏi obstacle_sprites.
		- Xử lý logic trao thưởng vũ khí mới khi clear màn.
		"""

		self.current_monsters = len([s for s in self.attackable_sprites if s.sprite_type != 'player_summon'])
		
		# Check for win condition / reward
		if self.current_monsters == 0 and self.total_monsters > 0 and getattr(self, 'reward_given', True) == False:
			self.reward_given = True
			self.reward_display_time = pygame.time.get_ticks()
			
			if self.current_map == 'first':
				self.reward_weapon = 'axe'
			elif self.current_map == 'second':
				self.reward_weapon = 'sai'
			elif self.current_map == 'fourth':
				self.reward_weapon = 'lance'
			else:
				self.reward_weapon = None
				
			if self.reward_weapon and self.reward_weapon not in self.player.unlocked_weapons:
				self.player.unlocked_weapons.append(self.reward_weapon)
		
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

	def display_reward_logic(self, events):
		if getattr(self, 'reward_weapon', None) and hasattr(self, 'reward_display_time') and self.reward_display_time > 0:
			current_time = pygame.time.get_ticks()
			if current_time - self.reward_display_time < 4000: # 4 seconds
				self.ui.show_reward(self.reward_weapon)
				
				# Allow skip after 500ms
				if current_time - self.reward_display_time > 500:
					for event in events:
						if event.type == pygame.KEYDOWN:
							self.reward_display_time = 0
			else:
				self.reward_display_time = 0

	def round_elapsed_seconds(self):
		return (pygame.time.get_ticks() - self.round_start_time) // 1000

	def total_elapsed_seconds(self):
		current_time = pygame.time.get_ticks()
		elapsed = current_time - self.start_time - self.pause_offset
		if self.show_skill_tree and self.skill_tree_pause_start:
			elapsed -= current_time - self.skill_tree_pause_start
		return max(0, elapsed) // 1000

	def _build_round_enemy_entries(self):
		counts = {}
		preview_images = {}
		for sprite in self.attackable_sprites:
			name = getattr(sprite, 'monster_name', None)
			if not name:
				continue
			counts[name] = counts.get(name, 0) + 1
			if name not in preview_images:
				preview_images[name] = sprite.image.copy()

		# Round 2 special briefing: Megumi + planned summons
		if self.current_map == 'second':
			def load_intro_image(path, scale):
				try:
					surf = pygame.image.load(path).convert_alpha()
					surf = remove_background_floodfill(surf, threshold = 40)
					return pygame.transform.scale_by(surf, scale)
				except:
					return None

			return [
				{
					'name': 'MEGUMI',
					'count': 1,
					'damage': int(monster_data['boss2']['damage']),
					'is_boss': True,
					'intro': 'Summoner BOSS controlling all shikigami on this map.',
					'image': preview_images.get('boss2') or load_intro_image('../graphics/megumi.png', 0.32)
				},
				{
					'name': 'DIVINE DOG (BLACK)',
					'count': 1,
					'damage': 8,
					'is_boss': False,
					'intro': 'Fast melee summons that pressure you at close range.',
					'image': load_intro_image('../graphics/summons/divine-dog-black.png', 0.13)
				},
				{
					'name': 'DIVINE DOG (WHITE)',
					'count': 1,
					'damage': 8,
					'is_boss': False,
					'intro': 'Fast melee summons that pressure you at close range.',
					'image': load_intro_image('../graphics/summons/divine-dog-white.png', 0.13)
				},
				{
					'name': 'FROG',
					'count': 4,
					'damage': 2,
					'is_boss': False,
					'intro': 'Special: attacks apply slow and make movement harder.',
					'image': load_intro_image('../graphics/summons/frog.png', 0.3)
				},
				{
					'name': 'BULL',
					'count': 1,
					'damage': 15,
					'is_boss': False,
					'intro': 'Special: heavy charge attack with strong knockback.',
					'image': load_intro_image('../graphics/summons/bull.png', 0.3)
				},
				{
					'name': 'TOTALITY DOG',
					'count': 1,
					'damage': 18,
					'is_boss': False,
					'intro': 'Evolved dog form with higher damage and sustain pressure.',
					'image': load_intro_image('../graphics/summons/totality-dog.png', 0.0975)
				}
			]

		entries = []
		for name, count in sorted(counts.items(), key = lambda kv: kv[0]):
			damage = int(monster_data.get(name, {}).get('damage', 0))
			entries.append({
				'name': name.upper().replace('-', ' '),
				'count': count,
				'damage': damage,
				'is_boss': name.startswith('boss'),
				'intro': self.enemy_intro_text.get(name, 'Hostile curse with basic attacks.'),
				'image': preview_images.get(name)
			})
		return entries

	def enqueue_round_intro(self, show_starter_weapon = False):
		self.intro_sequence = []
		if show_starter_weapon:
			magic_key = self.ui.get_key_label('MAGIC') if hasattr(self, 'ui') else pygame.key.name(CONTROLS['MAGIC']).upper()
			self.intro_sequence.append({
				'type': 'weapon',
				'weapon': 'sword',
				'title': 'STARTER WEAPON',
				'extra_lines': [
					f'Potion: press {magic_key} to heal.',
					'You start each run with 5 potions.'
				]
			})
		entries = self._build_round_enemy_entries()
		if entries:
			self.intro_sequence.append({
				'type': 'enemy_intro',
				'round': MAPS[self.current_map]['index'],
				'entries': entries
			})
		self.intro_active = len(self.intro_sequence) > 0
		now = pygame.time.get_ticks()
		self.intro_started_at = now
		# Prevent menu confirm key from instantly skipping first intro card
		self.intro_input_lock_until = now + 250

	def handle_intro_sequence(self, events):
		if not self.intro_active or not self.intro_sequence:
			self.intro_active = False
			return False

		now = pygame.time.get_ticks()
		if now < self.intro_input_lock_until:
			item = self.intro_sequence[0]
			if item['type'] == 'weapon':
				self.ui.show_reward(
					item['weapon'],
					title = item['title'],
					header = 'LOADOUT READY',
					extra_lines = item.get('extra_lines')
				)
			elif item['type'] == 'enemy_intro':
				self.ui.show_round_enemy_intro(item['round'], item['entries'])
			return True

		for event in events:
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				self.intro_sequence.pop(0)
				self.intro_started_at = now
				break

		if not self.intro_sequence:
			self.intro_active = False
			return False

		item = self.intro_sequence[0]
		if item['type'] == 'weapon':
			self.ui.show_reward(
				item['weapon'],
				title = item['title'],
				header = 'LOADOUT READY',
				extra_lines = item.get('extra_lines')
			)
		elif item['type'] == 'enemy_intro':
			self.ui.show_round_enemy_intro(item['round'], item['entries'])
		return True

	def _capture_leaderboard_on_death(self):
		"""Only rounds 2–4 count for leaderboard on death; time = since this round started."""
		idx = MAPS[self.current_map]['index']
		if idx < 2:
			self.pending_leaderboard = None
			return
		self.pending_leaderboard = {
			'round': f'Round {idx}',
			'time': self.round_elapsed_seconds()
		}

	def _capture_leaderboard_on_win(self):
		self.pending_leaderboard = {'round': 'Win', 'time': self.round_elapsed_seconds()}

	def _queue_leaderboard_save_from_pending(self):
		self._leaderboard_save_pending = self.pending_leaderboard
		self.pending_leaderboard = None

	def consume_leaderboard_save(self):
		"""Called by Game after run(); returns dict or None."""
		d = self._leaderboard_save_pending
		self._leaderboard_save_pending = None
		return d

	def restart_game(self):
		self._queue_leaderboard_save_from_pending()
		self.start_time = pygame.time.get_ticks()
		self.player.health = self.player.stats['health']
		self.player.target_health = self.player.health
		self.player.potions_left = self.player.max_potions
		self.player.unlocked_weapons = ['sword']
		self.player.weapon_index = 0
		self.player.weapon = self.player.unlocked_weapons[self.player.weapon_index]
		self.player.vulnerable = True
		self.player.frozen = False
		self.game_over_selection = 0
		self.win_selection = 0
		self.status = 'playing'
		self.switch_map('first')
		self.enqueue_round_intro(show_starter_weapon = True)

	def game_over_logic(self, events):
		self.ui.show_game_over(self.game_over_selection)
		
		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_a or event.key == pygame.K_LEFT:
					self.game_over_selection = 0
				elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
					self.game_over_selection = 1
				elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
					if self.game_over_selection == 0:
						self.restart_game()
					elif self.game_over_selection == 1:
						self._queue_leaderboard_save_from_pending()
						self.status = 'back_to_menu'

	def win_logic(self, events):
		self.ui.show_win(self.win_selection)
		
		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_a or event.key == pygame.K_LEFT:
					self.win_selection = 0
				elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
					self.win_selection = 1
				elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
					if self.win_selection == 0:
						self.restart_game()
					elif self.win_selection == 1:
						self._queue_leaderboard_save_from_pending()
						self.status = 'back_to_menu'

	def run(self, events=None):
		if events is None: events = []

		for event in events:
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				if self.show_skill_tree:
					self.show_skill_tree = False
					if self.skill_tree_pause_start:
						self.pause_offset += pygame.time.get_ticks() - self.skill_tree_pause_start
						self.skill_tree_pause_start = 0
				elif self.status == 'playing' and not self.intro_active:
					self.show_skill_tree = True
					self.skill_tree_pause_start = pygame.time.get_ticks()
					self.skill_tree_mode = 'category'
					self.skill_tree_category_index = 0
					self.skill_tree_skill_index = 0

		# Intro cards are paused overlays: keep map background visible, wait for SPACE.
		if self.intro_active and self.intro_sequence:
			self.current_monsters = len(self.attackable_sprites)
			self.visible_sprites.custom_draw(self.player)
			self.ui.display(
				self.player,
				MAPS[self.current_map]['index'],
				self.current_monsters,
				self.total_monsters,
				self.total_elapsed_seconds()
			)
			self.handle_intro_sequence(events)
			return
		
		# Check for win condition
		if self.current_map == 'fourth' and self.current_monsters <= 0 and self.reward_given:
			if self.status != 'win':
				self.status = 'win'
				self._capture_leaderboard_on_win()
			self.visible_sprites.custom_draw(self.player)
			self.win_logic(events)
			return

		if hasattr(self, 'player') and self.player.health <= 0:
			if self.status != 'game_over':
				self.status = 'game_over'
				self._capture_leaderboard_on_death()
				self._game_over_hud_seconds = self.total_elapsed_seconds()
			self.visible_sprites.custom_draw(self.player)
			self.ui.display(self.player, MAPS[self.current_map]['index'], self.current_monsters, self.total_monsters, self._game_over_hud_seconds)
			self.game_over_logic(events)
			return
		
		self.status = 'playing'

		if self.show_skill_tree:
			self.handle_skill_tree_input(events)
			self.current_monsters = len(self.attackable_sprites)
			self.visible_sprites.custom_draw(self.player)
			self.ui.display(
				self.player,
				MAPS[self.current_map]['index'],
				self.current_monsters,
				self.total_monsters,
				self.total_elapsed_seconds()
			)
			self.ui.draw_skill_tree(
				self.player,
				self.skill_tree_category_index,
				self.skill_tree_skill_index,
				self.skill_tree_mode,
				self
			)
			return

		# Wire boss2 summon references once player is ready
		if hasattr(self, '_pending_boss2') and self._pending_boss2 and hasattr(self, 'player'):
			b2 = self._pending_boss2
			b2._summon_groups  = [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites]
			b2._summon_player  = self.player
			b2._summon_damage  = self.damage_player
			b2._summon_animation_player = self.animation_player
			self._pending_boss2 = None

		# update and draw the game
		# Process telegraphs
		current_time = pygame.time.get_ticks()
		for telegraph in self.telegraphs[:]:
			if current_time >= telegraph['time']:
				telegraph['callback'](*telegraph['args'])
				self.telegraphs.remove(telegraph)

		# Sai Weapon Mechanic: Summon/Despawn dogs
		if self.player.weapon == 'sai' and self.player.last_weapon != 'sai':
			# Switch TO Sai: Summon dogs
			from summon import DivineDog
			for variant, data in self.player.sai_dogs_data.items():
				if data['alive']:
					dog = DivineDog(
						variant = variant,
						owner = self.player,
						player = self.player,
						groups = [self.visible_sprites, self.attackable_sprites, self.obstacle_sprites], # So they block movement and can be hit
						obstacle_sprites = self.obstacle_sprites,
						damage_player = self.damage_player,
						animation_player = self.animation_player,
						is_player_owned = True,
						attackable_sprites = self.attackable_sprites
					)
					dog.health = data['health']
					self.player.sai_dogs_active.append(dog)
		elif self.player.weapon != 'sai' and self.player.last_weapon == 'sai':
			# Switch AWAY from Sai: Despawn dogs
			for dog in self.player.sai_dogs_active:
				if dog.alive():
					dog.begin_despawn()
			self.player.sai_dogs_active = []
		
		self.player.last_weapon = self.player.weapon

		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update()
		self.visible_sprites.enemy_update(self.player)
		self.player_attack_logic()
		self.enemy_attack_logic()
		self.update_gate_state()
		self.check_map_transition()
		elapsed_time = self.total_elapsed_seconds()
		self.ui.display(self.player, MAPS[self.current_map]['index'], self.current_monsters, self.total_monsters, elapsed_time)
		self.display_reward_logic(events)

		if self.handle_intro_sequence(events):
			return


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
			
		# draw health bars on top of all sprites
		for sprite in self.sprites():
			if hasattr(sprite, 'draw_health_bar'):
				sprite.draw_health_bar(self.display_surface, self.offset)

	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		targets = [player] + [s for s in self if getattr(s, 'sprite_type', '') == 'player_summon']
		for enemy in enemy_sprites:
			enemy.enemy_update(targets)