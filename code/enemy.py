import pygame
import random
import math
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
	def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, create_attack = None, destroy_attack = None):
		# general setup
		super().__init__(groups)
		self.sprite_type = 'enemy'

		# graphics setup
		self.monster_name = monster_name
		self.import_graphics(monster_name)
		self.status = 'idle'
		self.image = self.animations[self.status][self.frame_index]

		# movement
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-8)
		self.obstacle_sprites = obstacle_sprites

		# stats
		monster_info = monster_data[self.monster_name]
		self.health = monster_info['health']
		self.exp = monster_info['exp']
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
		distance = self.get_player_distance_direction(player)[0]
		current_time = pygame.time.get_ticks()

		# Check for initial delay
		if current_time - self.spawn_time < self.attack_delay:
			self.status = 'idle'
			return

		if self.attacking:
			if '_attack' not in self.status:
				if self.monster_name == 'boss':
					# Maintain previous attack direction status
					pass
				else:
					self.status = 'attack'
			return

		if distance <= self.attack_radius and self.can_attack:
			if 'attack' not in self.status:
				self.frame_index = 0
				# Determine direction for boss attack
				if self.monster_name == 'boss':
					direction = self.get_player_distance_direction(player)[1]
					if abs(direction.x) > abs(direction.y):
						self.status = 'right_attack' if direction.x > 0 else 'left_attack'
					else:
						self.status = 'down_attack' if direction.y > 0 else 'up_attack'
					
					# Start attack sequence like player
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
					if self.create_attack:
						self.create_attack(self)
				else:
					self.status = 'attack'
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
					self.damage_player(self.attack_damage, self.attack_type)
					
		elif distance <= self.notice_radius:
			if self.monster_name == 'boss':
				direction = self.get_player_distance_direction(player)[1]
				if abs(direction.x) > abs(direction.y):
					self.status = 'right_move' if direction.x > 0 else 'left_move'
				else:
					self.status = 'down_move' if direction.y > 0 else 'up_move'
			else:
				self.status = 'move'
		else:
			if self.monster_name == 'boss':
				if 'move' in self.status: self.status = self.status.replace('move', 'idle')
				elif 'attack' not in self.status: self.status = 'down_idle'
			else:
				self.status = 'idle'

	def actions(self, player):
		if self.attacking:
			self.direction = pygame.math.Vector2()
		elif 'move' in self.status:
			self.direction = self.get_player_distance_direction(player)[1]
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

		self.rect = self.image.get_rect(center = self.hitbox.center)

		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		
		if self.attacking:
			if current_time - self.attack_time >= self.attack_duration:
				self.attacking = False
				if self.monster_name == 'boss' and self.destroy_attack:
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
			self.direction = self.get_player_distance_direction(player)[1]
			if attack_type == 'weapon':
				self.health -= player.get_full_weapon_damage()
			elif attack_type == 'magic':
				# self.health -= player.get_full_magic_damage()
				pass
			self.hit_time = pygame.time.get_ticks()
			self.vulnerable = False

	def check_death(self):
		if self.health <= 0:
			if self.monster_name == 'boss' and self.destroy_attack:
				self.destroy_attack(self)
			self.kill()

	def hit_reaction(self):
		if not self.vulnerable:
			self.direction *= -self.resistance

	def update(self):
		self.hit_reaction()
		self.move(self.speed)
		self.animate()
		self.cooldowns()
		self.check_death()

	def enemy_update(self, player):
		self.get_status(player)
		self.actions(player)
