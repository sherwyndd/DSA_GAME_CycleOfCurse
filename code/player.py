import pygame 
import os
import math
from settings import *
from support import *
from entity import Entity

class GhostNode:
	def __init__(self, surf, rect, alpha):
		self.surf = surf.copy()
		self.rect = rect.copy()
		self.alpha = alpha
		self.next = None

class Player(Entity):
	def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack):
		super().__init__(groups)
		
		# character setup
		self.char_config = {
			1: {'name': 'Monkey', 'img': 'monkey.png', 'walk': 'monkey-walk.png', 'scale': 0.4},
			2: {'name': 'Megumi', 'img': 'megumi.png', 'walk': None, 'scale': 0.32},
			3: {'name': 'Sukuna', 'img': 'sukuna.png', 'walk': None, 'scale': 0.32}
		}
		self.player_index = PLAYER_INDEX
		
		# graphics setup
		self.import_player_assets()
		self.status = 'down_idle'
		self.frame_index = 0
		self.animation_speed = 0.15
		self.image = self.animations[self.status][self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, -8)


		# movement 
		self.direction = pygame.math.Vector2()
		self.speed = 5
		self.attacking = False
		self.attack_type = None # 'attack' or 'dash'
		self.attack_time = None
		self.action_duration = 250 
		self.obstacle_sprites = obstacle_sprites

		# weapon
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		self.weapon_index = WEAPON_INDEX
		self.weapon = list(weapon_data.keys())[self.weapon_index]
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.switch_duration_cooldown = 500

		# magic 
		self.create_magic = None # Will be set in Level
		self.magic_index = 0
		self.magic = list(magic_data.keys())[self.magic_index]
		self.can_switch_magic = True
		self.magic_switch_time = None


		# cooldowns
		self.can_attack = True
		self.can_dash = True
		self.can_cast_magic = True
		self.attack_cooldown_duration = 200
		self.dash_cooldown_duration = 2000
		self.magic_cooldown_duration = 200
		self.attack_cooldown_time = 0
		self.dash_cooldown_time = 0
		self.magic_cooldown_time = 0

		# stats
		self.stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 5}
		self.health = 50
		self.target_health = self.health
		self.energy = self.stats['energy'] * 1
		self.exp = 1

		# ghost effect (Linked List)
		self.ghost_head = None # Head of our Linked List
		self.ghost_timer = 0
		self.ghost_frequency = 5 # Create a ghost every 5 frames

		# damage timer
		self.vulnerable = True
		self.hurt_time = None
		self.invulnerability_duration = 500

	# Flood fill moved to support.py

	def slice_spritesheet(self, path, cols, rows, scale):
		try:
			sheet = pygame.image.load(path).convert_alpha()
			sheet = remove_background_floodfill(sheet)
			w = sheet.get_width() // cols
			h = sheet.get_height() // rows
			frames = []
			for r in range(rows):
				for c in range(cols):
					rect = pygame.Rect(c * w, r * h, w, h)
					frame = sheet.subsurface(rect).copy()
					frame = pygame.transform.scale_by(frame, scale) 
					frames.append(frame)
			return frames
		except:
			return []

	def import_player_assets(self):
		self.animations = {
			'idle': [], 'up': [], 'down': [], 'left': [], 'right': [], 
			'right_idle' :[], 'left_idle' :[], 'up_idle' :[], 'down_idle' :[], 
			'attack': [], 'dash': [] 
		}

		config = self.char_config.get(self.player_index, self.char_config[1])
		char_path = '../graphics/' + config['img']
		walk_path = '../graphics/' + config['walk'] if config['walk'] else None
		scale = config['scale']

		try:
			idle_surf = pygame.image.load(char_path).convert_alpha()
			idle_surf = remove_background_floodfill(idle_surf)
			idle_surf = pygame.transform.scale_by(idle_surf, scale)
		except:
			idle_surf = pygame.Surface((64,64)); idle_surf.fill('red')

		if walk_path:
			walk_frames = self.slice_spritesheet(walk_path, 4, 1, scale)
		else:
			walk_frames = [idle_surf]

		flipped_idle = pygame.transform.flip(idle_surf, True, False)
		flipped_walk = [pygame.transform.flip(f, True, False) for f in walk_frames]

		self.animations['idle'] = [idle_surf]
		self.animations['down_idle'] = [idle_surf]; self.animations['up_idle'] = [idle_surf]
		self.animations['right_idle'] = [idle_surf]; self.animations['left_idle'] = [flipped_idle]
		self.animations['right'] = walk_frames; self.animations['left'] = flipped_walk
		self.animations['up'] = walk_frames; self.animations['down'] = walk_frames
		self.animations['attack'] = [idle_surf]; self.animations['dash'] = [idle_surf]

	def get_movement_input(self):
		if self.attacking: return

		keys = pygame.key.get_pressed()

		# movement input
		if keys[pygame.K_w]: self.direction.y = -1; self.status = 'up'
		elif keys[pygame.K_s]: self.direction.y = 1; self.status = 'down'
		else: self.direction.y = 0

		if keys[pygame.K_d]: self.direction.x = 1; self.status = 'right'
		elif keys[pygame.K_a]: self.direction.x = -1; self.status = 'left'
		else: self.direction.x = 0

	def get_attack_input(self):
		if self.attacking: return
		keys = pygame.key.get_pressed()

		# attack input
		if keys[pygame.K_SPACE] and self.can_attack and self.direction.magnitude() == 0:
			self.attacking = True
			self.attack_type = 'attack'
			self.attack_time = pygame.time.get_ticks()
			self.create_attack()
			self.direction.x = 0; self.direction.y = 0

			
		# dash input
		if keys[pygame.K_LCTRL] and self.can_dash:
			self.attacking = True
			self.attack_type = 'dash'
			self.attack_time = pygame.time.get_ticks()
			self.frame_index = 0
			self.direction.x = 0; self.direction.y = 0

		# magic input
		if keys[pygame.K_z] and self.can_cast_magic and self.direction.magnitude() == 0:
			self.attacking = True
			self.attack_type = 'magic'
			self.attack_time = pygame.time.get_ticks()
			style = list(magic_data.keys())[self.magic_index]
			strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
			cost = list(magic_data.values())[self.magic_index]['cost']
			if self.create_magic:
				self.create_magic(style,strength,cost)

		# weapon switch input
		if keys[pygame.K_q] and self.can_switch_weapon:
			self.can_switch_weapon = False
			self.weapon_switch_time = pygame.time.get_ticks()
			
			if self.weapon_index < len(list(weapon_data.keys())) - 1:
				self.weapon_index += 1
			else:
				self.weapon_index = 0
				
			self.weapon = list(weapon_data.keys())[self.weapon_index]

	def get_status(self):
		if self.attacking:
			if '_attack' not in self.status and '_dash' not in self.status:
				self.status = self.status.split('_')[0] + '_' + self.attack_type
			return

		if self.direction.x == 0 and self.direction.y == 0:
			if 'idle' not in self.status:
				self.status = self.status.split('_')[0] + '_idle'

	def move(self,speed):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()
		
		lunge_vector = pygame.math.Vector2(0,0)
		if self.attacking and self.attack_type == 'dash':
			progress = (pygame.time.get_ticks() - self.attack_time) / self.action_duration
			sin_val = math.sin(progress * math.pi)
			offset = sin_val * 15
			if 'left' in self.status: lunge_vector.x = -offset
			elif 'right' in self.status: lunge_vector.x = offset
			elif 'up' in self.status: lunge_vector.y = -offset
			elif 'down' in self.status: lunge_vector.y = offset

		self.hitbox.x += (self.direction.x * speed) + lunge_vector.x
		self.collision("horizontal")
		self.hitbox.y += (self.direction.y * speed) + lunge_vector.y
		self.collision("vertical")
		self.rect.center = self.hitbox.center

	def collision(self,direction):
		if direction == "horizontal":
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0 or 'right' in self.status: self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0 or 'left' in self.status: self.hitbox.left = sprite.hitbox.right
		if direction == "vertical":
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0 or 'down' in self.status: self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0 or 'up' in self.status: self.hitbox.top = sprite.hitbox.bottom

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		
		if self.attacking:
			if current_time - self.attack_time >= self.action_duration:
				self.attacking = False
				if self.attack_type == 'attack':
					self.destroy_attack()
					self.can_attack = False
					self.attack_cooldown_time = current_time
				elif self.attack_type == 'dash':
					self.can_dash = False
					self.dash_cooldown_time = current_time
				elif self.attack_type == 'magic':
					self.can_cast_magic = False
					self.magic_cooldown_time = current_time

		if not self.can_attack:
			if current_time - self.attack_cooldown_time >= self.attack_cooldown_duration:
				self.can_attack = True
		
		if not self.can_dash:
			if current_time - self.dash_cooldown_time >= self.dash_cooldown_duration:
				self.can_dash = True

		if not self.can_switch_weapon:
			if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True

		if not self.can_cast_magic:
			if current_time - self.magic_cooldown_time >= self.magic_cooldown_duration:
				self.can_cast_magic = True

		if not self.vulnerable:
			if current_time - self.hurt_time >= self.invulnerability_duration:
				self.vulnerable = True

	def animate(self):
		base_status = self.status.split('_')[0]
		if base_status in ['attack', 'dash']: base_status = 'down'
		
		animation = self.animations.get(self.status, self.animations.get(base_status, self.animations['idle']))
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation): self.frame_index = 0

		image = animation[int(self.frame_index)]
		
		# dash leaning effect
		if self.attacking and self.attack_type == 'dash':
			angle = 0
			if 'left' in self.status: angle = -15
			elif 'right' in self.status: angle = 15
			elif 'up' in self.status: angle = 5
			elif 'down' in self.status: angle = -5
			image = pygame.transform.rotate(image, angle)

		self.image = image
		self.rect = self.image.get_rect(center = self.hitbox.center)

		# flicker 
		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def update_ghosts(self):
		# 1. Thêm bóng ma mới (Chỉ khi đang lướt - DASH)
		is_dashing = self.attacking and self.attack_type == 'dash'
		
		# Tăng tần suất bóng ma khi lướt (mỗi 2 frame thay vì 5)
		frequency = 2 if is_dashing else self.ghost_frequency

		if is_dashing and self.ghost_timer % frequency == 0:
			new_node = GhostNode(self.image, self.rect, 150)
			new_node.next = self.ghost_head
			self.ghost_head = new_node
		
		self.ghost_timer = (self.ghost_timer + 1) % 60 # Dùng mod 60 cho timer chung

		# 2. Cập nhật và Xóa bóng ma mờ (Traverse and Prune)
		current = self.ghost_head
		prev = None
		while current:
			current.alpha -= 10 # Tốc độ tan biến
			if current.alpha <= 0:
				# Xóa nút này khỏi danh sách
				if prev:
					prev.next = None # Cắt đuôi
				else:
					self.ghost_head = None # Xóa sạch nếu là đầu
				break # Vì chúng ta thêm vào đầu, nên các nút sau chắc chắn mờ hơn
			
			current.surf.set_alpha(current.alpha)
			prev = current
			current = current.next

	def draw_ghosts(self, surface, offset):
		current = self.ghost_head
		while current:
			offset_pos = current.rect.topleft - offset
			surface.blit(current.surf, offset_pos)
			current = current.next

	def get_full_weapon_damage(self):
		base_damage = self.stats['attack']
		weapon_damage = weapon_data[self.weapon]['damage']
		return base_damage + weapon_damage

	def update(self):
		self.get_movement_input()
		self.move(self.speed)
		self.get_attack_input()
		self.cooldowns()
		self.get_status()
		self.animate()

		# gradual healing
		if self.health < self.target_health:
			self.health += (self.target_health - self.health) / 50 # smooth transition (approx 2.5s)
			if self.target_health - self.health < 0.1:
				self.health = self.target_health

		# ghost update
		self.update_ghosts()
