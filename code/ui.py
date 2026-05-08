import pygame
from settings import * 
from support import remove_background_floodfill

class UI:
	def __init__(self):
		
		# general 
		self.display_surface = pygame.display.get_surface()
		self.font = pygame.font.Font(UI_FONT,UI_FONT_SIZE)

		# bar setup 
		self.health_bar_rect = pygame.Rect(10,10,HEALTH_BAR_WIDTH,BAR_HEIGHT)
		self.energy_bar_rect = pygame.Rect(10,34,ENERGY_BAR_WIDTH,BAR_HEIGHT)
		self.monster_bar_rect = pygame.Rect(WIDTH // 2 - MONSTER_BAR_WIDTH // 2, 10, MONSTER_BAR_WIDTH, BAR_HEIGHT)

		# convert weapon dictionary
		self.weapon_graphics = []
		for weapon in weapon_data.values():
			path = weapon['graphic']
			weapon_surf = pygame.image.load(path).convert_alpha()
			weapon_surf = remove_background_floodfill(weapon_surf, threshold = 40)
			self.weapon_graphics.append(weapon_surf)

		# convert magic dictionary
		self.magic_graphics = []
		for magic in magic_data.values():
			magic_surf = pygame.image.load(magic['graphic']).convert_alpha()
			magic_surf = remove_background_floodfill(magic_surf, threshold = 40)
			magic_surf = pygame.transform.scale(magic_surf, (50, 50))
			self.magic_graphics.append(magic_surf)


	def show_bar(self,current,max_amount,bg_rect,color, target_amount = None, border_radius = 5):
		# draw bg 
		pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect, border_radius = border_radius)

		# drawing target/faint bar
		if target_amount and target_amount > current:
			target_ratio = target_amount / max_amount
			target_width = bg_rect.width * target_ratio
			target_rect = bg_rect.copy()
			target_rect.width = target_width
			# Faint color (e.g., darker red for health)
			faint_color = '#770000' if color == HEALTH_COLOR else color
			pygame.draw.rect(self.display_surface,faint_color,target_rect, border_radius = border_radius)

		# converting stat to pixel
		if max_amount > 0:
			ratio = current / max_amount
		else:
			ratio = 0
		current_width = bg_rect.width * ratio
		current_rect = bg_rect.copy()
		current_rect.width = current_width

		# drawing the bar
		if current_width > 0:
			pygame.draw.rect(self.display_surface,color,current_rect, border_radius = border_radius)
		pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3, border_radius = border_radius)

	def show_monster_count(self, current, total):
		if total > 0:
			self.show_bar(current, total, self.monster_bar_rect, MONSTER_COLOR, border_radius = 10)
			
			# Add text for monster count
			text_surf = self.font.render(f'{current}/{total}', False, TEXT_COLOR)
			text_rect = text_surf.get_rect(center = self.monster_bar_rect.center)
			self.display_surface.blit(text_surf, text_rect)

	def show_map_index(self,index):
		text_surf = self.font.render(f'MAP: {index}',False,TEXT_COLOR)
		x = self.display_surface.get_size()[0] - 20
		y = self.display_surface.get_size()[1] - 20
		text_rect = text_surf.get_rect(bottomright = (x,y))

		pygame.draw.rect(self.display_surface,UI_BG_COLOR,text_rect.inflate(20,20))
		self.display_surface.blit(text_surf,text_rect)
		pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,text_rect.inflate(20,20),3)

	def selection_box(self,left,top, has_switched):
		bg_rect = pygame.Rect(left,top,ITEM_BOX_SIZE,ITEM_BOX_SIZE)
		pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)
		if has_switched:
			pygame.draw.rect(self.display_surface,UI_BORDER_COLOR_ACTIVE,bg_rect,3)
		else:
			pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)
		return bg_rect

	def show_key_label(self, text, box_rect):
		text_surf = self.font.render(text, False, TEXT_COLOR)
		text_rect = text_surf.get_rect(topleft = box_rect.topleft + pygame.math.Vector2(5,5))
		self.display_surface.blit(text_surf, text_rect)

	def weapon_overlay(self,weapon_index,has_switched):
		bg_rect = self.selection_box(10,610,has_switched) 
		weapon_surf = self.weapon_graphics[weapon_index]
		weapon_rect = weapon_surf.get_rect(center = bg_rect.center)
		self.display_surface.blit(weapon_surf,weapon_rect)
		self.show_key_label('Q', bg_rect)

	def magic_overlay(self,magic_index,has_switched):
		bg_rect = self.selection_box(80,615,has_switched) 
		magic_surf = self.magic_graphics[magic_index]
		magic_rect = magic_surf.get_rect(center = bg_rect.center)
		self.display_surface.blit(magic_surf,magic_rect)
		self.show_key_label('Z', bg_rect)

	def display(self,player,map_index, monster_count, total_monsters):
		self.show_bar(player.health,player.stats['health'],self.health_bar_rect,HEALTH_COLOR, player.target_health)
		self.show_bar(player.energy,player.stats['energy'],self.energy_bar_rect,ENERGY_COLOR)
		self.show_monster_count(monster_count, total_monsters)

		self.show_map_index(map_index)

		self.weapon_overlay(player.weapon_index,not player.can_switch_weapon)
		self.magic_overlay(player.magic_index,not player.can_switch_magic)
