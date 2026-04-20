import pygame 
from settings import *

class Tile(pygame.sprite.Sprite):
	def __init__(self,pos,groups):
		super().__init__(groups)
		self.image = pygame.Surface((T_WIDTH, T_HEIGHT), pygame.SRCALPHA)
        # Không fill màu gì cả, hoặc fill màu có độ trong suốt bằng 0
        # (0, 0, 0, 0) -> Đỏ, Lục, Lam, Alpha (Alpha = 0 là tàng hình hoàn toàn)
		self.image.fill((0, 0, 0, 0)) 
        # Rect vẫn đóng vai trò là khung va chạm (obstacle)
		self.rect = self.image.get_rect(topleft = pos)