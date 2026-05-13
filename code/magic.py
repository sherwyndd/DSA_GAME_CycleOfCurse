import pygame
import math
from settings import *

class GhostNode:
	"""
	Node đơn trong Linked List lưu một afterimage của SukunaSlash.

	Attributes:
		surf (pygame.Surface): Bản sao Surface của slash tại thời điểm tạo node.
		rect (pygame.Rect): Vị trí tại thời điểm tạo node.
		alpha (int): Độ trong suốt hiện tại (giảm dần mỗi frame).
		next (GhostNode | None): Node tiếp theo trong danh sách liên kết.
	"""

	def __init__(self, surf, rect, alpha):
		self.surf = surf.copy()
		self.rect = rect.copy()
		self.alpha = alpha
		self.surf.set_alpha(alpha)
		self.next = None

class SukunaSlash(pygame.sprite.Sprite):
	"""
	Projectile đặc biệt của Sukuna (Dismantle).

	DSA Highlights:
	- Singly Linked List: Quản lý chuỗi bóng ma (Ghost trail) kéo dài sau đạn.
	- Sin Wave Scaling: Hiệu ứng Shimmer (nhấp nháy) kích thước procedurally.
	"""

	def __init__(self, pos, direction, groups, obstacle_sprites, animation_player, player, owner = None):
		super().__init__(groups)
		self.animation_player = animation_player
		self.obstacle_sprites = obstacle_sprites
		self.player = player 
		self.owner = owner 
		self.sprite_type = 'magic'
		self.damage = 15 
		
		# Load and Tint custom image
		try:
			full_path = '../graphics/energy-slash.png'
			self.base_image = pygame.image.load(full_path).convert_alpha()
			# Tint Red
			red_surf = pygame.Surface(self.base_image.get_size()).convert_alpha()
			red_surf.fill((255, 0, 0, 255))
			self.base_image.blit(red_surf, (0, 0), special_flags = pygame.BLEND_RGBA_MULT)
			# Scale to 1.5x player height
			target_height = int(player.rect.height * 1.5)
			current_height = self.base_image.get_height()
			scale_factor = target_height / current_height
			self.base_image = pygame.transform.scale_by(self.base_image, scale_factor)
		except:
			self.base_image = animation_player.frames['sukuna_slash'][0]

		# Direction and speed
		self.direction = direction
		self.speed = 7.5 # Tăng 1.5 lần (từ 5 -> 7.5)
		
		# Image setup based on direction
		self.image = self.base_image
		if direction.x != 0: # Horizontal
			if direction.x < 0: self.image = pygame.transform.flip(self.image, True, False)
		else: # Vertical
			angle = 90 if direction.y < 0 else 270
			self.image = pygame.transform.rotate(self.image, angle)
			
		self.rect = self.image.get_rect(center = pos)
		self.hitbox = self.rect.inflate(-6, -6) # Thu gọn nhẹ để không bị hụt đòn do quá mỏng
		self.spawn_time = pygame.time.get_ticks()
		self.duration = 12000 

		# Trail Logic (Ghosting - Linked List)
		self.ghost_head = None
		self.ghost_timer = 0
		self.ghost_frequency = 3 # Tần suất trung bình để các bóng "dãy với nhau"

	def update_ghosts(self):
		# 1. Thêm bóng ma mới
		if self.ghost_timer % self.ghost_frequency == 0:
			new_node = GhostNode(self.image, self.rect, 130)
			new_node.next = self.ghost_head
			self.ghost_head = new_node
		
		self.ghost_timer = (self.ghost_timer + 1) % 60

		# 2. Cập nhật và Xóa bóng ma mờ
		current = self.ghost_head
		prev = None
		while current:
			current.alpha -= 10 # Tốc độ tan biến chậm hơn một chút để vệt dài ra
			if current.alpha <= 0:
				if prev: prev.next = None
				else: self.ghost_head = None
				break
			
			current.surf.set_alpha(current.alpha)
			prev = current
			current = current.next

	def update(self):
		if not self.groups(): return

		self.update_ghosts()

		# Animation lúc di chuyển: Hiệu ứng Shimmer (rung rinh/nhấp nháy)
		# Thay đổi nhẹ kích thước dựa trên sin wave
		shimmer = 1.0 + math.sin(pygame.time.get_ticks() * 0.02) * 0.05
		self.image = pygame.transform.scale_by(self.base_image, shimmer)
		
		# Cập nhật rotation lại vì self.image vừa bị scale đè lên
		if self.direction.x != 0:
			if self.direction.x < 0: self.image = pygame.transform.flip(self.image, True, False)
		else:
			angle = 90 if self.direction.y < 0 else 270
			self.image = pygame.transform.rotate(self.image, angle)

		# Movement
		self.hitbox.x += self.direction.x * self.speed
		self.hitbox.y += self.direction.y * self.speed
		self.rect.center = self.hitbox.center
		
		# Kill if too old
		if self.groups() and pygame.time.get_ticks() - self.spawn_time > self.duration:
			self.kill()

	def draw_ghosts(self, surface, offset):
		current = self.ghost_head
		while current:
			offset_pos = current.rect.topleft - offset
			surface.blit(current.surf, offset_pos)
			current = current.next

class MagicPlayer:
	def __init__(self,animation_player):
		self.animation_player = animation_player

	def heal(self,player,strength,cost,groups):
		"""
		Sử dụng Thức thần Khuyển Thần trắng để hồi máu.
		Giá trị hồi phục được cộng vào target_health để thanh HP Lerp mượt mà.
		"""

		player.target_health += strength
		if player.target_health >= player.stats['health']:
			player.target_health = player.stats['health']

	def dismantle(self, player, groups, obstacle_sprites):
		# Direction clamping to cardinal axis
		direction = pygame.math.Vector2()
		if 'left' in player.status: direction.x = -1
		elif 'right' in player.status: direction.x = 1
		elif 'up' in player.status: direction.y = -1
		elif 'down' in player.status: direction.y = 1
		
		if direction.magnitude() == 0: direction.y = 1 # default
		
		SukunaSlash(player.rect.center, direction, groups, obstacle_sprites, self.animation_player, player, owner = player)
