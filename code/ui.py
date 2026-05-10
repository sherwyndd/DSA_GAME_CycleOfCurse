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
		self.armor_bar_rect = pygame.Rect(10,34,ARMOR_BAR_WIDTH,BAR_HEIGHT)
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

		# Effect icons
		self.anti_heal_icon = pygame.image.load('../graphics/potion_antiheal.png').convert_alpha()
		self.anti_heal_icon = remove_background_floodfill(self.anti_heal_icon, threshold=40)
		self.anti_heal_icon = pygame.transform.scale(self.anti_heal_icon, (30, 30))
		# Tint it green
		green_surf = pygame.Surface(self.anti_heal_icon.get_size()).convert_alpha()
		green_surf.fill((0, 255, 0, 150))
		self.anti_heal_icon.blit(green_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

		self.ice_icon = pygame.image.load('../graphics/ice_icon.png').convert_alpha()
		self.ice_icon = remove_background_floodfill(self.ice_icon, threshold=40)
		self.ice_icon = pygame.transform.scale(self.ice_icon, (30, 30))


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

	def show_armor_bar(self, current, max_amount, bg_rect, color, border_radius = 5):
		# No background or border drawn here, just the colored rectangle of current width
		if max_amount > 0:
			ratio = current / max_amount
		else:
			ratio = 0
		
		current_width = bg_rect.width * ratio
		current_rect = bg_rect.copy()
		current_rect.width = current_width

		if current_width > 0:
			pygame.draw.rect(self.display_surface,color,current_rect, border_radius = border_radius)
			# Optional: very thin border or just leave it as is
			pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,current_rect,1, border_radius = border_radius)

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

	def weapon_overlay(self,weapon_name,has_switched):
		bg_rect = self.selection_box(10,610,has_switched) 
		weapon_index = list(weapon_data.keys()).index(weapon_name)
		weapon_surf = self.weapon_graphics[weapon_index]
		weapon_rect = weapon_surf.get_rect(center = bg_rect.center)
		self.display_surface.blit(weapon_surf,weapon_rect)
		self.show_key_label('Q', bg_rect)

	def show_reward(self, weapon_name):
		box_rect = pygame.Rect(0,0,400,250)
		box_rect.center = (WIDTH // 2, HEIGHT // 2)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect, border_radius = 10)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, box_rect, 4, border_radius = 10)
		
		text_surf = self.font.render('STAGE CLEARED!', False, TEXT_COLOR)
		text_rect = text_surf.get_rect(center = (box_rect.centerx, box_rect.top + 40))
		self.display_surface.blit(text_surf, text_rect)
		
		text_surf2 = self.font.render('NEW WEAPON UNLOCKED:', False, TEXT_COLOR)
		text_rect2 = text_surf2.get_rect(center = (box_rect.centerx, box_rect.top + 80))
		self.display_surface.blit(text_surf2, text_rect2)
		
		weapon_index = list(weapon_data.keys()).index(weapon_name)
		weapon_surf = self.weapon_graphics[weapon_index]
		weapon_surf = pygame.transform.scale_by(weapon_surf, 1.5)
		weapon_rect = weapon_surf.get_rect(center = (box_rect.centerx, box_rect.bottom - 60))
		self.display_surface.blit(weapon_surf, weapon_rect)
		
		name_surf = self.font.render(weapon_name.upper(), False, 'gold')
		name_rect = name_surf.get_rect(center = (box_rect.centerx, box_rect.bottom - 20))
		self.display_surface.blit(name_surf, name_rect)

	def magic_overlay(self,magic_index,has_switched,player):
		bg_rect = self.selection_box(80,615,has_switched) 
		magic_surf = self.magic_graphics[magic_index]
		
		if player.potions_left > 0:
			magic_rect = magic_surf.get_rect(center = bg_rect.center)
			self.display_surface.blit(magic_surf,magic_rect)
			
		self.show_key_label('Z', bg_rect)
		
		# Show potion count box
		count_box = pygame.Rect(bg_rect.right - 20, bg_rect.top - 10, 30, 30)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, count_box)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, count_box, 3)
		count_surf = self.font.render(str(player.potions_left), False, TEXT_COLOR)
		count_rect = count_surf.get_rect(center = count_box.center)
		self.display_surface.blit(count_surf, count_rect)

	def display(self,player,map_index, monster_count, total_monsters):
		self.show_bar(player.health,player.stats['health'],self.health_bar_rect,HEALTH_COLOR, player.target_health)
		self.show_armor_bar(player.armor,player.stats['armor'],self.armor_bar_rect,ARMOR_COLOR)
		self.show_monster_count(monster_count, total_monsters)

		self.show_map_index(map_index)

		self.weapon_overlay(player.weapon,not player.can_switch_weapon)
		self.magic_overlay(player.magic_index,not player.can_switch_magic,player)

		# Effect icons preview (Small box at top-left of weapon box)
		if player.weapon in ('sword', 'axe'):
			# Box dimensions
			box_size = 34
			# Flush against the top-left corner of the weapon box (10, 610)
			box_rect = pygame.Rect(10, 610 - box_size, box_size, box_size)
			
			pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect)
			pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, box_rect, 2)
			
			if player.weapon == 'sword':
				icon_rect = self.anti_heal_icon.get_rect(center = box_rect.center)
				self.display_surface.blit(self.anti_heal_icon, icon_rect)
			elif player.weapon == 'axe':
				icon_rect = self.ice_icon.get_rect(center = box_rect.center)
				self.display_surface.blit(self.ice_icon, icon_rect)

	def show_game_over(self, selection):
		overlay = pygame.Surface((WIDTH, HEIGHT))
		overlay.set_alpha(150)
		overlay.fill('black')
		self.display_surface.blit(overlay, (0,0))
		
		box_rect = pygame.Rect(0,0,500,300)
		box_rect.center = (WIDTH // 2, HEIGHT // 2)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect, border_radius = 10)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, box_rect, 4, border_radius = 10)
		
		title_font = pygame.font.Font(UI_FONT, 30)
		text_surf = title_font.render('YOU DIED', False, 'red')
		text_rect = text_surf.get_rect(center = (box_rect.centerx, box_rect.top + 60))
		self.display_surface.blit(text_surf, text_rect)
		
		btn_w, btn_h = 180, 60
		try_again_rect = pygame.Rect(0, 0, btn_w, btn_h)
		try_again_rect.center = (box_rect.centerx - 110, box_rect.bottom - 80)
		
		exit_rect = pygame.Rect(0, 0, btn_w, btn_h)
		exit_rect.center = (box_rect.centerx + 110, box_rect.bottom - 80)
		
		color0 = UI_BORDER_COLOR_ACTIVE if selection == 0 else UI_BORDER_COLOR
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, try_again_rect, border_radius = 5)
		pygame.draw.rect(self.display_surface, color0, try_again_rect, 3, border_radius = 5)
		try_surf = self.font.render('TRY AGAIN', False, TEXT_COLOR)
		try_rect = try_surf.get_rect(center = try_again_rect.center)
		self.display_surface.blit(try_surf, try_rect)
		
		color1 = UI_BORDER_COLOR_ACTIVE if selection == 1 else UI_BORDER_COLOR
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, exit_rect, border_radius = 5)
		pygame.draw.rect(self.display_surface, color1, exit_rect, 3, border_radius = 5)
		exit_surf = self.font.render('EXIT', False, TEXT_COLOR)
		exit_rect_text = exit_surf.get_rect(center = exit_rect.center)
		self.display_surface.blit(exit_surf, exit_rect_text)
