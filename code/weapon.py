import pygame 
from support import remove_background_floodfill

class Weapon(pygame.sprite.Sprite):
	def __init__(self,owner,groups):
		super().__init__(groups)
		self.owner = owner
		self.sprite_type = 'weapon'
		direction = owner.status.split('_')[0]

		# graphic
		full_path = f'../graphics/weapons/{owner.weapon}/{direction}.png'
		self.image = pygame.image.load(full_path).convert_alpha()
		self.image = remove_background_floodfill(self.image, threshold = 40)
		
		# scale 
		self.scale = 1.0 if getattr(owner, 'monster_name', None) == 'boss' else 0.84
		self.image = pygame.transform.scale_by(self.image, self.scale)
		
		# placement
		self.update_position()



		self.hitbox = self.rect

	def update_position(self):
		direction = self.owner.status.split('_')[0]
		
		# Boss offset logic: 10px further away
		is_boss = getattr(self.owner, 'monster_name', None) == 'boss'
		offset_x = 10 if is_boss else 0
		offset_y = -10 if is_boss else 0

		if direction == 'right':
			self.rect = self.image.get_rect(midleft = self.owner.rect.midright + pygame.math.Vector2(offset_x,16))
		elif direction == 'left': 
			self.rect = self.image.get_rect(midright = self.owner.rect.midleft + pygame.math.Vector2(-offset_x,16))
		elif direction == 'down':
			self.rect = self.image.get_rect(midtop = self.owner.rect.midbottom + pygame.math.Vector2(0,-offset_y))
		else: # up
			self.rect = self.image.get_rect(midbottom = self.owner.rect.midtop + pygame.math.Vector2(0,offset_y))
		
		self.hitbox = self.rect

	def update(self):
		self.update_position()