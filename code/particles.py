import pygame
from support import import_folder, remove_background_floodfill

class AnimationPlayer:
	"""
	Kho lưu trữ và factory cho tất cả hiệu ứng hạt trong game.

	DSA Highlights:
	- Dictionary Mapping: Lưu trữ frame theo loại hiệu ứng (Key-Value access O(1)).
	- Image Processing: Hỗ trợ Tint và Scale frame procedurally.
	"""

	def __init__(self):
		smoke_frames = import_folder('../graphics/particles/smoke')
		self.frames = {
			# hit particles (triggered when player takes damage)
			'thunder':  self.scale_frames(self.clean_frames(import_folder('../graphics/particles/thunder')), 0.6),   # spirit attacks player
			'frozen':   self.scale_frames(list(reversed(self.clean_frames(import_folder('../graphics/particles/frozen')))), 0.8),  # boss attacks player (3→0)

			# death particles (triggered when enemy dies)
			'spirit':   self.tint_frames(self.scale_frames(smoke_frames, 1.0), (255, 50, 50, 255)),   # Red
			'slime':    self.tint_frames(self.scale_frames(smoke_frames, 1.0), (0, 200, 255, 255)),   # Cyan
			'boss':     self.tint_frames(self.scale_frames(smoke_frames, 2.5), (150, 150, 150, 255)), # Gray
			'slash':    self.scale_frames(self.clean_frames(import_folder('../graphics/particles/slash')), 1.0),
			'frog_hit': self.tint_frames(self.scale_frames(smoke_frames, 0.7), (50, 180, 50, 200)), # Green mud/slime hit

			# Boss death particles
			'boss2':    self.tint_frames(self.scale_frames(smoke_frames, 2.5), (130, 80, 200, 255)),  # Purple (Megumi)
			'boss3':    self.tint_frames(self.scale_frames(smoke_frames, 2.5), (200, 30, 30, 255)),   # Crimson (Sukuna)

			# Weapon hit particles
			'lance':       self.tint_frames(self.scale_frames(self.clean_frames(import_folder('../graphics/particles/slash')), 1.2), (255, 80, 80, 255)),  # Red slash (center)
			'lance_small': self.tint_frames(self.scale_frames(self.clean_frames(import_folder('../graphics/particles/slash')), 0.7), (255, 80, 80, 200)),  # Smaller red slash (top/bottom)

			'flame': self.scale_frames(self.clean_frames(import_folder('../graphics/14 - upgrade/14 - upgrade/graphics/particles/flame/frames')), 1.0),
			'flame_warning': list(reversed(self.scale_frames(self.clean_frames(import_folder('../graphics/14 - upgrade/14 - upgrade/graphics/particles/flame/frames')), 1.0)[8:12])),
			'flame_erupt': list(reversed(self.scale_frames(self.clean_frames(import_folder('../graphics/14 - upgrade/14 - upgrade/graphics/particles/flame/frames')), 1.0)[0:8])),
			'claw': list(reversed(self.scale_frames(self.clean_frames(import_folder('../graphics/14 - upgrade/14 - upgrade/graphics/particles/claw')), 1.2))),
			'sukuna_slash': self.tint_frames(self.scale_frames(self.clean_frames(import_folder('../graphics/particles/slash')), 1.5), (255, 0, 0, 200)),
			'skeleton': self.tint_frames(self.scale_frames(smoke_frames, 1.0), (200, 200, 200, 255)),
			'skeleton-big': self.tint_frames(self.scale_frames(smoke_frames, 1.5), (200, 200, 200, 255)),
			'skeleton-shaman': self.tint_frames(self.scale_frames(smoke_frames, 1.2), (150, 100, 200, 255)),
		}

	def scale_frames(self, frames, scale):
		new_frames = []
		for frame in frames:
			new_frame = pygame.transform.scale_by(frame, scale)
			new_frames.append(new_frame)
		return new_frames

	def tint_frames(self, frames, color):
		new_frames = []
		for frame in frames:
			new_frame = frame.copy()
			new_frame.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
			new_frames.append(new_frame)
		return new_frames

	def reflect_images(self, frames):
		"""Flip frames horizontally – needed for boss since its frames are reversed vs spirit."""
		new_frames = []
		for frame in frames:
			flipped_frame = pygame.transform.flip(frame, True, False)
			new_frames.append(flipped_frame)
		return new_frames

	def clean_frames(self, frames):
		new_frames = []
		for frame in frames:
			cleaned_frame = remove_background_floodfill(frame.copy(), threshold=40)
			new_frames.append(cleaned_frame)
		return new_frames

	def create_particles(self, animation_type, pos, groups, pos_type='center'):
		if animation_type in self.frames:
			animation_frames = self.frames[animation_type]
			# frozen effect plays in 0.5s: 4 frames over 30 ticks (4/30 ≈ 0.133 per tick)
			speed = 4 / 30 if animation_type == 'frozen' else 0.15
			if animation_type == 'flame_warning': speed = 4 / 30 # 4 frames in 0.5s (30 ticks)
			if animation_type == 'flame_erupt': speed = 8 / 42   # 8 frames in 0.7s (42 ticks)
			ParticleEffect(pos, animation_frames, groups, animation_speed=speed, pos_type=pos_type)


class ParticleEffect(pygame.sprite.Sprite):
	def __init__(self, pos, animation_frames, groups, animation_speed=0.15, pos_type='center'):
		super().__init__(groups)
		self.frame_index = 0
		self.animation_speed = animation_speed
		self.frames = animation_frames
		self.image = self.frames[self.frame_index]
		self.pos_type = pos_type
		
		if self.pos_type == 'midbottom':
			self.rect = self.image.get_rect(midbottom=pos)
		else:
			self.rect = self.image.get_rect(center=pos)
		# Give ParticleEffect a hitbox so YSortCameraGroup depth-sorts correctly
		self.hitbox = self.rect

	def animate(self):
		self.frame_index += self.animation_speed
		if self.frame_index >= len(self.frames):
			self.kill()
		else:
			self.image = self.frames[int(self.frame_index)]
			if self.pos_type == 'midbottom':
				self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
			else:
				self.rect = self.image.get_rect(center=self.rect.center)
			self.hitbox = self.rect

	def update(self):
		self.animate()
