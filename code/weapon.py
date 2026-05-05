import pygame 

class Weapon(pygame.sprite.Sprite):
	def __init__(self,player,groups):
		super().__init__(groups)
		direction = player.status.split('_')[0]

		# graphic
		full_path = f'../graphics/weapons/{player.weapon}/{direction}.png'
		self.image = pygame.image.load(full_path).convert_alpha()
		
		# scale 
		self.image = pygame.transform.scale_by(self.image, 0.7)
		
		# placement
		if direction == 'right':
			self.rect = self.image.get_rect(midleft = player.rect.midright + pygame.math.Vector2(-10,16))
		elif direction == 'left': 
			self.rect = self.image.get_rect(midright = player.rect.midleft + pygame.math.Vector2(10,16))
		elif direction == 'down':
			self.rect = self.image.get_rect(midtop = player.rect.midbottom + pygame.math.Vector2(0,5))
		else: # up
			self.rect = self.image.get_rect(midbottom = player.rect.midtop + pygame.math.Vector2(0,-5))



		self.hitbox = self.rect