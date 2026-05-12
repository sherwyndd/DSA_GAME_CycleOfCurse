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

		# Status icons
		try:
			self.burn_icon = pygame.image.load('../graphics/14 - upgrade/14 - upgrade/graphics/particles/flame/frames/0.png').convert_alpha()
			self.burn_icon = remove_background_floodfill(self.burn_icon, threshold=40)
			self.burn_icon = pygame.transform.scale(self.burn_icon, (25, 25))
		except:
			self.burn_icon = pygame.Surface((25,25)); self.burn_icon.fill('orange')

		# Slow icon: purple spiral, compact height matching health bar
		import math
		sz = BAR_HEIGHT
		self.slow_icon = pygame.Surface((sz, sz), pygame.SRCALPHA)
		cx = cy = (sz - 1) * 0.5
		max_r = sz * 0.45
		purple = (180, 100, 240)
		stroke = (130, 60, 200)
		prev_pt = None
		steps = 56
		for i in range(steps):
			t = i / max(steps - 1, 1)
			angle = t * math.pi * 3.5
			r = t * max_r
			x = int(cx + r * math.cos(angle))
			y = int(cy + r * math.sin(angle))
			if prev_pt is not None:
				pygame.draw.line(self.slow_icon, stroke, prev_pt, (x, y), max(1, sz // 14))
			prev_pt = (x, y)
			if 0 <= x < sz and 0 <= y < sz:
				self.slow_icon.set_at((x, y), purple)


	def show_bar(self,current,max_amount,bg_rect,color, target_amount = None, border_radius = 5):
		# draw bg 
		pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect, border_radius = border_radius)

		# If target_amount is provided, we are doing a transition
		if target_amount is not None:
			# 1. HEALING: target > current
			# We show a dark version of the color representing where health is GOING
			if target_amount > current:
				target_ratio = target_amount / max_amount
				target_width = bg_rect.width * target_ratio
				target_rect = bg_rect.copy()
				target_rect.width = target_width
				faint_color = '#770000' if color == HEALTH_COLOR else color
				pygame.draw.rect(self.display_surface,faint_color,target_rect, border_radius = border_radius)
				
				# Then draw the current health on top
				ratio = current / max_amount
				current_width = bg_rect.width * ratio
				current_rect = bg_rect.copy()
				current_rect.width = current_width
				if current_width > 0:
					pygame.draw.rect(self.display_surface,color,current_rect, border_radius = border_radius)

			# 2. DAMAGE: target < current
			# We show current (the "ghost" bar) as a desaturated or white color, 
			# and target as the actual color
			else:
				# Draw the "ghost" bar (where health was)
				ratio = current / max_amount
				ghost_width = bg_rect.width * ratio
				ghost_rect = bg_rect.copy()
				ghost_rect.width = ghost_width
				ghost_color = '#EEEEEE' # White-ish ghost bar
				pygame.draw.rect(self.display_surface,ghost_color,ghost_rect, border_radius = border_radius)

				# Draw the "real" health (where health is now)
				target_ratio = target_amount / max_amount
				target_width = bg_rect.width * target_ratio
				target_rect = bg_rect.copy()
				target_rect.width = target_width
				if target_width > 0:
					pygame.draw.rect(self.display_surface,color,target_rect, border_radius = border_radius)
		else:
			# No transition, just draw normally
			ratio = current / max_amount
			current_width = bg_rect.width * ratio
			current_rect = bg_rect.copy()
			current_rect.width = current_width
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

	def show_timer(self, elapsed_seconds):
		# Format time as mm:ss
		minutes = int(elapsed_seconds // 60)
		seconds = int(elapsed_seconds % 60)
		time_str = f'{minutes:02}:{seconds:02}'
		
		# Position: Top right
		text_surf = self.font.render(time_str, False, TEXT_COLOR)
		x = self.display_surface.get_size()[0] - 20
		y = 20
		text_rect = text_surf.get_rect(topright = (x, y))
		
		# Draw background box
		box_rect = text_rect.inflate(20, 10)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect, border_radius = 5)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, box_rect, 3, border_radius = 5)
		
		# Draw text
		self.display_surface.blit(text_surf, text_rect)

	def display(self,player,map_index, monster_count, total_monsters, elapsed_time):
		self.show_bar(player.health,player.stats['health'],self.health_bar_rect,HEALTH_COLOR, player.target_health)
		self.show_armor_bar(player.armor,player.stats['armor'],self.armor_bar_rect,ARMOR_COLOR)
		self.show_monster_count(monster_count, total_monsters)
		self.show_timer(elapsed_time)

		self.show_map_index(map_index)

		self.weapon_overlay(player.weapon,not player.can_switch_weapon)
		self.magic_overlay(player.magic_index,not player.can_switch_magic,player)
		
		# Status effect icons next to health bar (vertically centered on bar)
		icon_x = self.health_bar_rect.right + 8
		
		if player.is_burning:
			icon_y = self.health_bar_rect.centery - self.burn_icon.get_height() // 2
			self.display_surface.blit(self.burn_icon, (icon_x, icon_y))
			icon_x += self.burn_icon.get_width() + 4
		
		if player.is_slowed:
			icon_y = self.health_bar_rect.centery - self.slow_icon.get_height() // 2
			self.display_surface.blit(self.slow_icon, (icon_x, icon_y))

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
		
		btn_w, btn_h = 220, 60
		try_again_rect = pygame.Rect(0, 0, btn_w, btn_h)
		try_again_rect.center = (box_rect.centerx - 120, box_rect.bottom - 80)
		
		exit_rect = pygame.Rect(0, 0, btn_w, btn_h)
		exit_rect.center = (box_rect.centerx + 120, box_rect.bottom - 80)
		
		color0 = UI_BORDER_COLOR_ACTIVE if selection == 0 else UI_BORDER_COLOR
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, try_again_rect, border_radius = 5)
		pygame.draw.rect(self.display_surface, color0, try_again_rect, 3, border_radius = 5)
		try_surf = self.font.render('TRY AGAIN', False, TEXT_COLOR)
		try_rect = try_surf.get_rect(center = try_again_rect.center)
		self.display_surface.blit(try_surf, try_rect)
		
		color1 = UI_BORDER_COLOR_ACTIVE if selection == 1 else UI_BORDER_COLOR
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, exit_rect, border_radius = 5)
		pygame.draw.rect(self.display_surface, color1, exit_rect, 3, border_radius = 5)
		exit_surf = self.font.render('BACK TO MENU', False, TEXT_COLOR)
		exit_rect_text = exit_surf.get_rect(center = exit_rect.center)
		self.display_surface.blit(exit_surf, exit_rect_text)

	def show_win(self, selection):
		overlay = pygame.Surface((WIDTH, HEIGHT))
		overlay.set_alpha(150)
		overlay.fill('black')
		self.display_surface.blit(overlay, (0,0))
		
		box_rect = pygame.Rect(0,0,600,350)
		box_rect.center = (WIDTH // 2, HEIGHT // 2)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect, border_radius = 15)
		pygame.draw.rect(self.display_surface, 'gold', box_rect, 5, border_radius = 15)
		
		title_font = pygame.font.Font(UI_FONT, 35)
		text_surf = title_font.render('CONGRATULATIONS!', False, 'gold')
		text_rect = text_surf.get_rect(center = (box_rect.centerx, box_rect.top + 60))
		self.display_surface.blit(text_surf, text_rect)
		
		sub_surf = self.font.render('YOU HAVE BEATEN THE CURSE', False, TEXT_COLOR)
		sub_rect = sub_surf.get_rect(center = (box_rect.centerx, box_rect.top + 110))
		self.display_surface.blit(sub_surf, sub_rect)
		
		btn_w, btn_h = 240, 60
		try_again_rect = pygame.Rect(0, 0, btn_w, btn_h)
		try_again_rect.center = (box_rect.centerx - 140, box_rect.bottom - 80)
		
		exit_rect = pygame.Rect(0, 0, btn_w, btn_h)
		exit_rect.center = (box_rect.centerx + 140, box_rect.bottom - 80)
		
		color0 = UI_BORDER_COLOR_ACTIVE if selection == 0 else UI_BORDER_COLOR
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, try_again_rect, border_radius = 5)
		pygame.draw.rect(self.display_surface, color0, try_again_rect, 3, border_radius = 5)
		try_surf = self.font.render('PLAY AGAIN', False, TEXT_COLOR)
		try_rect = try_surf.get_rect(center = try_again_rect.center)
		self.display_surface.blit(try_surf, try_rect)
		
		color1 = UI_BORDER_COLOR_ACTIVE if selection == 1 else UI_BORDER_COLOR
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, exit_rect, border_radius = 5)
		pygame.draw.rect(self.display_surface, color1, exit_rect, 3, border_radius = 5)
		exit_surf = self.font.render('BACK TO MENU', False, TEXT_COLOR)
		exit_rect_text = exit_surf.get_rect(center = exit_rect.center)
		self.display_surface.blit(exit_surf, exit_rect_text)
