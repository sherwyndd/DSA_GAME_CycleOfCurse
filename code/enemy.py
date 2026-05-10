import pygame
import math
import random
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
	def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles = None, create_attack = None, destroy_attack = None):
		# general setup
		super().__init__(groups)
		self.sprite_type = 'enemy'

		# graphics setup
		self.monster_name = monster_name
		self.import_graphics(monster_name)
		self.status = 'idle'
		self.image = self.animations[self.status][self.frame_index]

		# movement
		self.rect = self.image.get_rect(center = pos)
		self.hitbox = self.rect.inflate(0,-8)
		self.obstacle_sprites = obstacle_sprites

		# stats
		monster_info = monster_data[self.monster_name]
		self.health = monster_info['health']
		self.max_health = monster_info['health']
		self.speed = monster_info['speed']
		self.attack_damage = monster_info['damage']
		self.resistance = monster_info['resistance']
		self.attack_radius = monster_info['attack_radius']
		self.notice_radius = monster_info['notice_radius']
		self.attack_type = monster_info['attack_type']

		# player interaction
		self.can_attack = True
		self.attack_time = None
		self.attack_cooldown = 400
		self.damage_player = damage_player
		self.trigger_death_particles = trigger_death_particles

		self.vulnerable = True
		self.hit_time = None
		self.invincibility_duration = 300

		# attack
		self.can_attack = True
		self.spawn_time = pygame.time.get_ticks()
		self.attack_delay = 750

		# boss attack setup
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		self.attacking = False
		self.attack_duration = 250
		self.attack_cooldown_duration = 800
		self.attack_cooldown_time = 0
		if self.monster_name == 'boss':
			self.weapon = 'axe'
		if self.monster_name == 'boss2':
			self.weapon = 'sai'
			self.mana = 200
			self.max_mana = 200
			self._summons = []              # live DivineDog sprites
			self._summon_aggro_flag = False  # set True → dogs chase player
			self._summon_groups  = None     # set by Level
			self._summon_player  = None     # set by Level
			self._summon_damage  = None     # set by Level
			self._summon_animation_player = None # set by Level
			self._summon_cost    = 80       # mana per summon event
			self._mana_regen     = 12       # mana per second (Increased from 4)
			self._last_mana_tick = pygame.time.get_ticks()
			self._dead_summons   = set()    # track 'black', 'white', 'totality', 'bull', 'frog'
			self._fusion_active  = False
			self._frog_deaths    = 0        # frog can resummon once (total 2 lives)
			self._last_heal_tick = pygame.time.get_ticks()
			
			# Weapon effects
			self.anti_heal_time = 0
			self.anti_heal_duration = 3000
			self.frozen = False
			self.freeze_time = 0
			self.freeze_duration = 500 # 0.5s freeze for axe effect

		# freeze effect
		self.frozen = False
		self.freeze_time = 0
		self.freeze_duration = 200

	def import_graphics(self, name):
		if name == 'boss':
			self.animations = {
				'idle': [], 'move': [], 'attack': [],
				'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
				'up_move': [], 'down_move': [], 'left_move': [], 'right_move': [],
				'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': []
			}
			path = f'../graphics/cursed_spirits/boss-round-1.png'
			surf = pygame.image.load(path).convert_alpha()
			surf = remove_background_floodfill(surf, threshold = 40)
			surf = pygame.transform.scale_by(surf, 0.48) # Boss is 1.2x larger than previous (0.4 * 1.2)
			
			flipped_surf = pygame.transform.flip(surf, True, False)
			
			for key in self.animations.keys():
				if 'left' in key: self.animations[key] = [flipped_surf]
				else: self.animations[key] = [surf]
			return

		if name == 'boss2':
			self.animations = {
				'idle': [], 'move': [], 'attack': [],
				'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
				'up_move': [], 'down_move': [], 'left_move': [], 'right_move': [],
				'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': []
			}
			path = f'../graphics/megumi.png'
			surf = pygame.image.load(path).convert_alpha()
			surf = remove_background_floodfill(surf, threshold = 40)
			surf = pygame.transform.scale_by(surf, 0.32)

			flipped_surf = pygame.transform.flip(surf, True, False)

			# Generate human-like walk frames: slight up/down bob + left-right lean
			def make_walk_frames(base_surf, flipped=False):
				frames = []
				src = base_surf.copy()
				for i in range(6):
					t = i / 6.0
					import math
					# Vertical bob: move image up/down by cutting bottom/adding transparent
					bob = int(math.sin(t * math.pi * 2) * 3)
					frame_w = src.get_width()
					frame_h = src.get_height()
					frame = pygame.Surface((frame_w, frame_h + 6), pygame.SRCALPHA)
					frame.blit(src, (0, 3 + bob))  # offset so bob goes both up and down
					# Slight lean (scale_x tweak)
					lean = 1.0 + math.sin(t * math.pi * 2) * 0.02
					frame = pygame.transform.scale(frame, (int(frame_w * lean), frame_h + 6))
					# Crop back to original height to keep size stable
					cropped = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
					cropped.blit(frame, (-(frame.get_width() - frame_w) // 2, 0))
					frames.append(cropped)
				return frames

			idle_right = [surf]
			idle_left  = [flipped_surf]
			walk_right = make_walk_frames(surf, flipped=False)
			walk_left  = make_walk_frames(flipped_surf, flipped=True)

			for key in self.animations.keys():
				if 'left' in key:
					if 'move' in key: self.animations[key] = walk_left
					else:             self.animations[key] = idle_left
				else:
					if 'move' in key: self.animations[key] = walk_right
					else:             self.animations[key] = idle_right
			return

		if name == 'slime':
			self.animations = {
				'idle': [], 'move': [], 'attack': [],
				'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
				'up_move': [], 'down_move': [], 'left_move': [], 'right_move': [],
				'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': []
			}
			path_red = f'../graphics/cursed_spirits/slime.png'
			path_ice = f'../graphics/cursed_spirits/slime_lightblue.png'
			
			surf_red = pygame.image.load(path_red).convert_alpha()
			surf_red = remove_background_floodfill(surf_red, threshold = 40)
			surf_red = pygame.transform.scale_by(surf_red, 0.35) 
			
			surf_ice = pygame.image.load(path_ice).convert_alpha()
			surf_ice = remove_background_floodfill(surf_ice, threshold = 40)
			surf_ice = pygame.transform.scale_by(surf_ice, 0.35) 

			flipped_red = pygame.transform.flip(surf_red, True, False)
			flipped_ice = pygame.transform.flip(surf_ice, True, False)
			
			for key in self.animations.keys():
				if 'left' in key:
					if 'idle' in key: self.animations[key] = [flipped_red]
					else: self.animations[key] = [flipped_ice]
				else:
					if 'idle' in key: self.animations[key] = [surf_red]
					else: self.animations[key] = [surf_ice]
			return

		self.animations = {'idle':[], 'move':[], 'attack':[]}
		main_path = f'../graphics/monsters/{name}/'
		for animation in self.animations.keys():
			full_path = main_path + animation
			self.animations[animation] = import_folder(full_path)
			
			# Scale animations (1.5x larger than the previous 0.5 scale = 0.75)
			scaled_animation = []
			for surf in self.animations[animation]:
				scaled_surf = pygame.transform.scale_by(surf, 0.75)
				scaled_animation.append(scaled_surf)
			self.animations[animation] = scaled_animation

		# If no animations were found (e.g. folder empty or missing)
		if not self.animations['idle']:
			# Fallback
			sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
			pygame.draw.circle(sprite, (80, 20, 120), (16, 16), 12)
			self.animations = {
				'idle': [sprite],
				'move': [sprite],
				'attack': [sprite]
			}

	def get_player_distance_direction(self, player):
		enemy_vec = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(player.rect.center)
		distance = (player_vec - enemy_vec).magnitude()

		if distance > 0:
			direction = (player_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2()

		return (distance, direction)

	def get_status(self, player):
		if self.frozen:
			if self.monster_name == 'boss2':
				# Megumi's Technique Abrogation: Immediately break freeze with an attack
				self.frozen = False
				if self.can_attack:
					# Force an attack immediately
					distance, direction = self.get_player_distance_direction(player)
					if abs(direction.x) > abs(direction.y):
						self.status = 'right_attack' if direction.x > 0 else 'left_attack'
					else:
						self.status = 'down_attack' if direction.y > 0 else 'up_attack'
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
					if self.create_attack: self.create_attack(self)
				return
			else:
				self.status = 'idle'
				return

		distance = self.get_player_distance_direction(player)[0]
		current_time = pygame.time.get_ticks()

		# Check for initial delay
		if current_time - self.spawn_time < self.attack_delay:
			self.status = 'idle'
			return

		if self.attacking:
			if '_attack' not in self.status:
				if self.monster_name in ['boss', 'boss2', 'slime']:
					# Maintain previous attack direction status
					pass
				else:
					self.status = 'attack'
			return

		if distance <= self.attack_radius and self.can_attack:
			if 'attack' not in self.status:
				self.frame_index = 0
				# Determine direction for boss/boss2/slime attack
				if self.monster_name in ['boss', 'boss2', 'slime']:
					direction = self.get_player_distance_direction(player)[1]
					if abs(direction.x) > abs(direction.y):
						self.status = 'right_attack' if direction.x > 0 else 'left_attack'
					else:
						self.status = 'down_attack' if direction.y > 0 else 'up_attack'
					
					# Start attack sequence
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
					if self.monster_name in ['boss', 'boss2'] and self.create_attack:
						self.create_attack(self)
					else:
						self.damage_player(self.attack_damage, self.attack_type)
				else:
					self.status = 'attack'
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
					self.damage_player(self.attack_damage, self.attack_type)
					
		elif distance <= self.notice_radius:
			if self.monster_name in ['boss', 'boss2', 'slime']:
				direction = self.get_player_distance_direction(player)[1]
				if abs(direction.x) > abs(direction.y):
					self.status = 'right_move' if direction.x > 0 else 'left_move'
				else:
					self.status = 'down_move' if direction.y > 0 else 'up_move'
			else:
				self.status = 'move'
		else:
			if self.monster_name in ['boss', 'boss2', 'slime']:
				if 'move' in self.status: self.status = self.status.replace('move', 'idle')
				elif 'attack' not in self.status: self.status = 'down_idle'
			else:
				self.status = 'idle'

	def actions(self, player):
		if self.frozen:
			self.direction = pygame.math.Vector2()
			return

		if self.attacking:
			self.direction = pygame.math.Vector2()
		elif 'move' in self.status:
			self.direction = self.get_bfs_direction(player)
		else:
			self.direction = pygame.math.Vector2()

	def animate(self):
		animation = self.animations[self.status]
		
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		self.image = animation[int(self.frame_index)]
		
		# Boss movement effect: Squash and Stretch bobbing
		if self.monster_name == 'boss' and 'move' in self.status:
			bob = math.sin(pygame.time.get_ticks() * 0.015) * 0.05
			self.image = pygame.transform.scale_by(self.image, (1.0 + bob, 1.0 - bob))
		elif self.monster_name == 'boss2' and 'move' in self.status:
			# Human-like walk: subtle vertical bounce
			bob = math.sin(pygame.time.get_ticks() * 0.02) * 0.04
			self.image = pygame.transform.scale_by(self.image, (1.0, 1.0 + bob))
		elif self.monster_name == 'slime' and 'move' in self.status:
			bob = math.sin(pygame.time.get_ticks() * 0.02) * 0.1
			self.image = pygame.transform.scale_by(self.image, (1.0 + bob, 1.0 - bob))

		if self.frozen:
			# Apply ice tint
			ice_surf = pygame.Surface(self.image.get_size()).convert_alpha()
			ice_surf.fill((100, 200, 255, 120)) # Light blue with transparency
			self.image = self.image.copy()
			self.image.blit(ice_surf, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

		self.rect = self.image.get_rect(center = self.hitbox.center)

		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def draw_health_bar(self, surface, offset):
		bar_width = int(self.rect.width * 0.75)
		bar_height = 6
		bar_gap = 3
		
		# Health bar
		hp_bg = pygame.Rect(0, 0, bar_width, bar_height)
		hp_bg.midbottom = (self.rect.midtop[0], self.rect.midtop[1] - 1)
		hp_bg.topleft -= offset
		
		health_ratio = max(0, self.health / self.max_health)
		hp_rect = pygame.Rect(hp_bg.left, hp_bg.top, bar_width * health_ratio, bar_height)
		
		pygame.draw.rect(surface, 'red', hp_bg)
		pygame.draw.rect(surface, 'green', hp_rect)
		pygame.draw.rect(surface, 'black', hp_bg, 1)
		
		# Mana bar (only for boss2)
		if self.monster_name == 'boss2' and hasattr(self, 'mana'):
			mp_bg = pygame.Rect(hp_bg.left, hp_bg.bottom + bar_gap, bar_width, bar_height)
			
			mana_ratio = max(0, self.mana / self.max_mana)
			mp_rect = pygame.Rect(mp_bg.left, mp_bg.top, bar_width * mana_ratio, bar_height)
			
			pygame.draw.rect(surface, '#1a1a4e', mp_bg)  # Dark blue background
			pygame.draw.rect(surface, '#3399ff', mp_rect)  # Bright blue mana
			pygame.draw.rect(surface, 'black', mp_bg, 1)

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		
		if self.frozen:
			if current_time - self.freeze_time >= self.freeze_duration:
				self.frozen = False

		if self.attacking:
			if current_time - self.attack_time >= self.attack_duration:
				self.attacking = False
				if self.monster_name in ['boss', 'boss2'] and self.destroy_attack:
					self.destroy_attack(self)
				self.can_attack = False
				self.attack_cooldown_time = current_time

		if not self.can_attack:
			if current_time - self.attack_cooldown_time >= self.attack_cooldown_duration:
				self.can_attack = True

		if not self.vulnerable:
			if current_time - self.hit_time >= self.invincibility_duration:
				self.vulnerable = True

	def get_damage(self, player, attack_type):
		if self.vulnerable:
			self.direction = self.get_player_direction(player)
			if attack_type == 'weapon':
				self.health -= player.get_full_weapon_damage()
				
				# Weapon effects
				now = pygame.time.get_ticks()
				if player.weapon == 'sword':
					self.anti_heal_time = now
				elif player.weapon == 'axe':
					if random.random() < 1.0: # Increased to 100% for testing
						self.freeze()
						# Spawn frozen particles at enemy position
						if self._summon_animation_player:
							frozen_pos = (self.rect.midbottom[0], self.rect.midbottom[1] + 20)
							self._summon_animation_player.create_particles('frozen', frozen_pos, [self._summon_groups[0]], pos_type='midbottom')
						
			elif attack_type == 'magic':
				pass
			self.hit_time = pygame.time.get_ticks()
			self.vulnerable = False

	def freeze(self):
		self.frozen = True
		self.freeze_time = pygame.time.get_ticks()
		self.direction = pygame.math.Vector2()

	def get_player_direction(self, player):
		enemy_vec = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(player.rect.center)
		distance = (player_vec - enemy_vec).magnitude()
		if distance > 0:
			return (player_vec - enemy_vec).normalize()
		return pygame.math.Vector2()

	def get_bfs_direction(self, player):
		from collections import deque
		start_c = int(self.rect.centerx // T_WIDTH)
		start_r = int(self.rect.centery // T_HEIGHT)
		target_c = int(player.rect.centerx // T_WIDTH)
		target_r = int(player.rect.centery // T_HEIGHT)

		grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
		
		# Mark obstacles (tiles and other enemies so they flank each other)
		for sprite in self.obstacle_sprites:
			if sprite is self or sprite is player:
				continue
				
			left_c = int(sprite.hitbox.left // T_WIDTH)
			right_c = int((sprite.hitbox.right - 1) // T_WIDTH)
			top_r = int(sprite.hitbox.top // T_HEIGHT)
			bottom_r = int((sprite.hitbox.bottom - 1) // T_HEIGHT)
			
			for r in range(top_r, bottom_r + 1):
				for c in range(left_c, right_c + 1):
					if 0 <= r < ROWS and 0 <= c < COLS:
						grid[r][c] = 1

		# Ensure start and target are always reachable in the grid
		if 0 <= start_c < COLS and 0 <= start_r < ROWS:
			grid[start_r][start_c] = 0
		if 0 <= target_c < COLS and 0 <= target_r < ROWS:
			grid[target_r][target_c] = 0

		queue = deque([(start_c, start_r)])
		visited = {(start_c, start_r): None}
		found = False

		while queue:
			curr_c, curr_r = queue.popleft()
			if curr_c == target_c and curr_r == target_r:
				found = True
				break

			for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
				nc, nr = curr_c + dc, curr_r + dr
				if 0 <= nc < COLS and 0 <= nr < ROWS:
					if grid[nr][nc] == 0 and (nc, nr) not in visited:
						if dc != 0 and dr != 0:
							if grid[curr_r][nc] == 1 or grid[nr][curr_c] == 1:
								continue
						visited[(nc, nr)] = (curr_c, curr_r)
						queue.append((nc, nr))

		if found:
			curr = (target_c, target_r)
			path = []
			while curr != (start_c, start_r):
				path.append(curr)
				curr = visited[curr]
			path.reverse()

			if path:
				next_c, next_r = path[0]
				target_pixel = pygame.math.Vector2((next_c + 0.5) * T_WIDTH, (next_r + 0.5) * T_HEIGHT)
				my_pixel = pygame.math.Vector2(self.rect.center)
				direction = target_pixel - my_pixel
				if direction.magnitude() > 0:
					return direction.normalize()
					
		return self.get_player_direction(player)

	def summon_aggro(self):
		"""Called when a divine dog is hit — makes all dogs attack."""
		if self.monster_name == 'boss2':
			self._summon_aggro_flag = True

	def summon_update(self):
		"""Mana regen + summon DivineDogs when mana is full."""
		if self.monster_name != 'boss2': return
		if self._summon_groups is None: return

		from summon import DivineDog
		now = pygame.time.get_ticks()

		# Mana regen
		dt = (now - self._last_mana_tick) / 1000.0
		self._last_mana_tick = now
		self.mana = min(self.max_mana, self.mana + self._mana_regen * dt)

		# Reset aggro flag each frame (dogs read it during their own update)
		# Keep it True only for one frame so dogs can read it
		# We store it for 1 frame then clear
		if hasattr(self, '_aggro_clear_next') and self._aggro_clear_next:
			self._summon_aggro_flag = False
			self._aggro_clear_next  = False
		if self._summon_aggro_flag:
			self._aggro_clear_next = True

		# Prune dead summons and track for fusion
		still_alive = []
		for s in self._summons:
			if s.alive():
				still_alive.append(s)
			else:
				# Dog just died - track it
				if s.variant in ('black', 'white', 'totality', 'bull', 'frog'):
					if s.variant == 'frog':
						self._frog_deaths += 1
						if self._frog_deaths >= 2: # frog dies permanently after 2 summons
							self._dead_summons.add('frog')
					else:
						self._dead_summons.add(s.variant)
		self._summons = still_alive

		# Fusion Check: If both black and white have died at least once
		if not self._fusion_active and 'black' in self._dead_summons and 'white' in self._dead_summons:
			self._fusion_active = True
			# Despawn any normal dogs immediately to make room for Totality
			for s in self._summons:
				if s.variant in ('black', 'white'):
					s.begin_despawn()

		# Summon Logic
		if self.mana >= self._summon_cost:
			if self._fusion_active:
				# Fusion mode: Summon ONE Totality dog ONLY ONCE
				existing_variants = [s.variant for s in self._summons]
				if 'totality' not in existing_variants and 'totality' not in self._dead_summons:
					dog = DivineDog(
						variant      = 'totality',
						owner        = self,
						player       = self._summon_player,
						groups       = self._summon_groups,
						obstacle_sprites = self.obstacle_sprites,
						damage_player   = self._summon_damage,
						animation_player = self._summon_animation_player
					)
					self._summons.append(dog)
					self.mana -= self._summon_cost * 1.5 # Totality costs more
			else:
				# Normal mode: Maintain 2 dogs (Black and White)
				if len(self._summons) < 2:
					slots_needed = 2 - len(self._summons)
					variants     = ['white', 'black']
					existing_variants = [s.variant for s in self._summons]
					for v in variants:
						if slots_needed <= 0 or self.mana < self._summon_cost: break
						# CRITICAL: Only summon if not already alive AND hasn't died yet
						if v not in existing_variants and v not in self._dead_summons:
							dog = DivineDog(
								variant      = v,
								owner        = self,
								player       = self._summon_player,
								groups       = self._summon_groups,
								obstacle_sprites = self.obstacle_sprites,
								damage_player   = self._summon_damage,
								animation_player = self._summon_animation_player
							)
							self._summons.append(dog)
							self.mana -= self._summon_cost
							slots_needed -= 1
					
					# Additional summons: Frog and Bull
					existing_variants = [s.variant for s in self._summons]
					
					# Bull: Summon once if mana allows and not yet dead
					if 'bull' not in existing_variants and 'bull' not in self._dead_summons and self.mana >= self._summon_cost * 1.2:
						from summon import Bull
						bull = Bull(self, self._summon_player, self._summon_groups, self.obstacle_sprites, self._summon_damage, self._summon_animation_player)
						self._summons.append(bull)
						self.mana -= self._summon_cost * 1.2
						
					# Frog: Summon if mana allows and not dead (dead means 2 deaths)
					if 'frog' not in existing_variants and 'frog' not in self._dead_summons and self.mana >= self._summon_cost * 0.8:
						from summon import Frog
						frog = Frog(self, self._summon_player, self._summon_groups, self.obstacle_sprites, self._summon_damage, self._summon_animation_player)
						self._summons.append(frog)
						self.mana -= self._summon_cost * 0.8

	def check_death(self):
		if self.health <= 0:
			# Despawn all summons
			for s in getattr(self, '_summons', []):
				if s.alive():
					s.begin_despawn()
			if hasattr(self, 'destroy_attack') and self.destroy_attack:
				self.destroy_attack(self)
			if self.trigger_death_particles:
				self.trigger_death_particles(self.rect.center, self.monster_name)
			self.kill()

	def hit_reaction(self):
		if not self.vulnerable:
			self.direction *= -self.resistance
		# When boss2 is hit, make summons aggressive
		if self.monster_name == 'boss2' and not self.vulnerable:
			self._summon_aggro_flag = True

	def update(self):
		self.hit_reaction()
		self.move(self.speed)
		self.animate()
		self.cooldowns()
		self.summon_update()
		self.check_death()

	def enemy_update(self, player):
		self.get_status(player)
		self.actions(player)
