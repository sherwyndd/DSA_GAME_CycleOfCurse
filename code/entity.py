import pygame
from math import sin

class Entity(pygame.sprite.Sprite):
	def __init__(self,groups):
		super().__init__(groups)
		self.frame_index = 0
		self.animation_speed = 0.15
		self.direction = pygame.math.Vector2()

	def move(self,speed):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal')
		self.hitbox.y += self.direction.y * speed
		self.collision('vertical')
		
		# Map boundary clamping (1224x711)
		if self.hitbox.left < 0: self.hitbox.left = 0
		if self.hitbox.right > 1224: self.hitbox.right = 1224
		if self.hitbox.top < 0: self.hitbox.top = 0
		if self.hitbox.bottom > 711: self.hitbox.bottom = 711
		
		self.rect.center = self.hitbox.center

	def collision(self,direction):
		if direction == 'horizontal':
			for sprite in self.obstacle_sprites:
				if sprite is not self and sprite.hitbox.colliderect(self.hitbox):
					# Use the smallest overlap to determine the collision side
					overlap_left = self.hitbox.right - sprite.hitbox.left
					overlap_right = sprite.hitbox.right - self.hitbox.left
					if overlap_left < overlap_right:
						self.hitbox.right = sprite.hitbox.left
					else:
						self.hitbox.left = sprite.hitbox.right

		if direction == 'vertical':
			for sprite in self.obstacle_sprites:
				if sprite is not self and sprite.hitbox.colliderect(self.hitbox):
					overlap_top = self.hitbox.bottom - sprite.hitbox.top
					overlap_bottom = sprite.hitbox.bottom - self.hitbox.top
					if overlap_top < overlap_bottom:
						self.hitbox.bottom = sprite.hitbox.top
					else:
						self.hitbox.top = sprite.hitbox.bottom

	def wave_value(self):
		value = sin(pygame.time.get_ticks())
		if value >= 0:
			return 255
		else:
			return 0
