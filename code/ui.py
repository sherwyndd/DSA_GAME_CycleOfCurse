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
		self.monster_bar_rect = pygame.Rect(WIDTH - MONSTER_BAR_WIDTH - 20, 10, MONSTER_BAR_WIDTH, BAR_HEIGHT)

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

		# English ability text for weapon info popups
		self.weapon_ability_text = {
			'sword': 'Anti-heal: enemies cannot regenerate for a short time.',
			'lance': 'No special status effect. Heavy damage with long cooldown.',
			'axe': 'Freeze chance: can briefly freeze enemies.',
			'rapier': 'No special status effect. Very fast light attacks.',
			'sai': 'No special status effect. Balanced speed and damage.'
		}


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

		# Add text: current / max
		hp_font = pygame.font.Font(UI_FONT, 12)
		hp_text = f"{int(current)} / {int(max_amount)}"
		hp_surf = hp_font.render(hp_text, False, TEXT_COLOR)
		hp_rect = hp_surf.get_rect(midleft = (bg_rect.right + 10, bg_rect.centery))
		self.display_surface.blit(hp_surf, hp_rect)

	def show_armor_bar(self, current, max_amount, bg_rect, color, border_radius = 5):
		# Draw background
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect, border_radius = border_radius)
		
		if max_amount > 0:
			ratio = current / max_amount
		else:
			ratio = 0
		
		current_width = bg_rect.width * ratio
		current_rect = bg_rect.copy()
		current_rect.width = current_width

		if current_width > 0:
			pygame.draw.rect(self.display_surface,color,current_rect, border_radius = border_radius)
		
		pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,2, border_radius = border_radius)

		# Add text: armor value
		arm_font = pygame.font.Font(UI_FONT, 12)
		arm_text = f"GIÁP: {int(current)}"
		arm_surf = arm_font.render(arm_text, False, TEXT_COLOR)
		arm_rect = arm_surf.get_rect(midleft = (bg_rect.right + 10, bg_rect.centery))
		self.display_surface.blit(arm_surf, arm_rect)

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

	def fit_font_to_width(self, text, max_width, max_size = 18, min_size = 12):
		size = max_size
		while size >= min_size:
			font = pygame.font.Font(UI_FONT, size)
			if font.size(text)[0] <= max_width:
				return font
			size -= 1
		return pygame.font.Font(UI_FONT, min_size)

	def selection_box(self,left,top, has_switched):
		bg_rect = pygame.Rect(left,top,ITEM_BOX_SIZE,ITEM_BOX_SIZE)
		pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)
		if has_switched:
			pygame.draw.rect(self.display_surface,UI_BORDER_COLOR_ACTIVE,bg_rect,3)
		else:
			pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)
		return bg_rect

	def get_key_label(self, action):
		key_val = CONTROLS.get(action)
		if key_val is None:
			return '??'
		return pygame.key.name(key_val).upper()

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
		self.show_key_label(self.get_key_label('SWITCH'), bg_rect)

	def show_reward(self, weapon_name, title='NEW WEAPON UNLOCKED', header='STAGE CLEARED!', extra_lines=None):
		box_rect = pygame.Rect(0,0,600,360)
		box_rect.center = (WIDTH // 2, HEIGHT // 2)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect, border_radius = 10)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, box_rect, 4, border_radius = 10)
		
		text_surf = self.font.render(header, False, TEXT_COLOR)
		text_rect = text_surf.get_rect(center = (box_rect.centerx, box_rect.top + 36))
		self.display_surface.blit(text_surf, text_rect)
		
		text_surf2 = self.font.render(f'{title}:', False, TEXT_COLOR)
		text_rect2 = text_surf2.get_rect(center = (box_rect.centerx, box_rect.top + 76))
		self.display_surface.blit(text_surf2, text_rect2)
		
		weapon_index = list(weapon_data.keys()).index(weapon_name)
		weapon_surf = self.weapon_graphics[weapon_index]
		weapon_surf = pygame.transform.scale_by(weapon_surf, 1.3)
		weapon_rect = weapon_surf.get_rect(center = (box_rect.centerx, box_rect.top + 136))
		self.display_surface.blit(weapon_surf, weapon_rect)
		
		name_surf = self.font.render(weapon_name.upper(), False, 'gold')
		name_rect = name_surf.get_rect(center = (box_rect.centerx, box_rect.top + 196))
		self.display_surface.blit(name_surf, name_rect)

		damage = weapon_data[weapon_name]['damage']
		cooldown = weapon_data[weapon_name]['cooldown']
		base_lines = [
			f'DMG: {damage}',
			f'Cooldown: {cooldown} ms',
			f'Ability: {self.weapon_ability_text.get(weapon_name, "No special effect.")}'
		]
		potion_lines = list(extra_lines) if extra_lines else []

		def wrap_text_for_font(text, max_width, font_obj):
			words = text.split(' ')
			out = []
			current = ''
			for w in words:
				test = w if not current else f'{current} {w}'
				if font_obj.size(test)[0] <= max_width:
					current = test
				else:
					if current:
						out.append(current)
					current = w
			if current:
				out.append(current)
			return out

		# Sword card inside the main reward box
		cards_top = box_rect.top + 222
		cards_bottom = box_rect.bottom - 14
		cards_height = cards_bottom - cards_top
		left_margin = box_rect.left + 18
		right_margin = box_rect.right - 18

		sword_card = pygame.Rect(left_margin, cards_top, right_margin - left_margin, cards_height)
		pygame.draw.rect(self.display_surface, (18, 18, 18), sword_card, border_radius = 8)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, sword_card, 2, border_radius = 8)

		# Auto-shrink sword text to avoid overflow.
		text_area_w = sword_card.width - 20
		text_area_h = sword_card.height - 16
		render_font = self.font
		rendered_lines = []
		for size in [18, 16, 14, 12]:
			font_obj = pygame.font.Font(UI_FONT, size)
			candidate = []
			for line in base_lines:
				candidate.extend(wrap_text_for_font(line, text_area_w, font_obj))
			line_h = font_obj.get_height() + 4
			if len(candidate) * line_h <= text_area_h:
				render_font = font_obj
				rendered_lines = candidate
				break
		if not rendered_lines:
			rendered_lines = []
			for line in base_lines:
				rendered_lines.extend(wrap_text_for_font(line, text_area_w, render_font))

		sy = sword_card.top + 8
		line_h = render_font.get_height() + 4
		max_lines = max(1, text_area_h // line_h)
		for line in rendered_lines[:max_lines]:
			line_surf = render_font.render(line, False, TEXT_COLOR)
			self.display_surface.blit(line_surf, (sword_card.left + 10, sy))
			sy += line_h

		if potion_lines:
			potion_card = pygame.Rect(box_rect.left + 18, box_rect.bottom + 12, box_rect.width - 36, 130)
			pygame.draw.rect(self.display_surface, (24, 24, 24), potion_card, border_radius = 8)
			pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, potion_card, 2, border_radius = 8)

			potion_title = self.font.render('POTION', False, 'gold')
			self.display_surface.blit(potion_title, (potion_card.left + 8, potion_card.top + 6))

			if self.magic_graphics:
				icon = pygame.transform.scale(self.magic_graphics[0], (26, 26))
				self.display_surface.blit(icon, (potion_card.right - 34, potion_card.top + 6))

			p_font = pygame.font.Font(UI_FONT, 14)
			py = potion_card.top + 38
			max_w = potion_card.width - 12
			line_h2 = p_font.get_height() + 4
			max_lines2 = max(1, (potion_card.height - 44) // line_h2)
			p_lines = []
			for line in potion_lines:
				p_lines.extend(wrap_text_for_font(line, max_w, p_font))
			for line in p_lines[:max_lines2]:
				line_surf = p_font.render(line, False, '#dcdcdc')
				self.display_surface.blit(line_surf, (potion_card.left + 6, py))
				py += line_h2

	def show_round_enemy_intro(self, round_index, entries):
		def wrap_text(text, max_width, font):
			words = text.split(' ')
			lines = []
			current = ''
			for w in words:
				test = w if not current else f'{current} {w}'
				if font.size(test)[0] <= max_width:
					current = test
				else:
					if current:
						lines.append(current)
					current = w
			if current:
				lines.append(current)
			return lines

		title_font = pygame.font.Font(UI_FONT, 26)
		title_bg = pygame.Rect(80, 18, WIDTH - 160, 56)
		pygame.draw.rect(self.display_surface, (20, 20, 20), title_bg, border_radius = 10)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, title_bg, 3, border_radius = 10)
		title_surf = title_font.render(f'ROUND {round_index} - ENEMY INTEL', False, 'gold')
		title_rect = title_surf.get_rect(center = title_bg.center)
		self.display_surface.blit(title_surf, title_rect)

		count = max(1, len(entries))
		if count >= 5:
			cols = 3
		elif count > 2:
			cols = 2
		else:
			cols = count
		rows = (count + cols - 1) // cols
		margin_x = 42
		gap_x = 14
		gap_y = 14
		card_w = (WIDTH - margin_x * 2 - gap_x * (cols - 1)) // cols
		top = 92
		bottom_reserved = 38
		card_h = (HEIGHT - top - bottom_reserved - gap_y * (rows - 1)) // rows
		body_font = pygame.font.Font(UI_FONT, 16)

		for i, entry in enumerate(entries):
			r = i // cols
			c = i % cols
			x = margin_x + c * (card_w + gap_x)
			y = top + r * (card_h + gap_y)
			card = pygame.Rect(x, y, card_w, card_h)

			pygame.draw.rect(self.display_surface, (26, 26, 26), card, border_radius = 10)
			pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, card, 2, border_radius = 10)

			image_box = pygame.Rect(card.left + 14, card.top + 14, card_w - 28, int(card_h * 0.45))
			pygame.draw.rect(self.display_surface, (14, 14, 14), image_box, border_radius = 8)

			img = entry.get('image')
			if img:
				max_w = image_box.width - 12
				max_h = image_box.height - 12
				scale = min(max_w / max(1, img.get_width()), max_h / max(1, img.get_height()), 1.0)
				draw_img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				img_rect = draw_img.get_rect(center = image_box.center)
				self.display_surface.blit(draw_img, img_rect)

			name_prefix = '[BOSS] ' if entry.get('is_boss') else ''
			name_text = f"{name_prefix}{entry['name']} x{entry['count']}"
			name_surf = body_font.render(name_text, False, 'gold' if entry.get('is_boss') else TEXT_COLOR)
			self.display_surface.blit(name_surf, (card.left + 14, image_box.bottom + 10))

			dmg_surf = body_font.render(f"DMG: {entry['damage']}", False, '#d8d8d8')
			self.display_surface.blit(dmg_surf, (card.left + 14, image_box.bottom + 34))

			intro_lines = wrap_text(entry['intro'], card_w - 28, body_font)
			intro_start_y = image_box.bottom + 56
			max_intro_lines = max(1, (card.bottom - 8 - intro_start_y) // 18)
			for li, line in enumerate(intro_lines[:max_intro_lines]):
				ls = body_font.render(line, False, '#b5b5b5')
				self.display_surface.blit(ls, (card.left + 14, intro_start_y + li * 18))

		hint_bg = pygame.Rect(WIDTH // 2 - 210, HEIGHT - 34, 420, 26)
		pygame.draw.rect(self.display_surface, (20, 20, 20), hint_bg, border_radius = 8)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, hint_bg, 2, border_radius = 8)
		hint_surf = self.font.render('Press SPACE to continue', False, '#bbbbbb')
		hint_rect = hint_surf.get_rect(center = hint_bg.center)
		self.display_surface.blit(hint_surf, hint_rect)

	def magic_overlay(self,magic_index,has_switched,player):
		# Place the potion slot right next to the weapon slot without gap
		bg_rect = self.selection_box(90,610,has_switched)
		magic_surf = self.magic_graphics[magic_index]
		
		if player.potions_left > 0:
			magic_rect = magic_surf.get_rect(center = bg_rect.center)
			self.display_surface.blit(magic_surf,magic_rect)
			
		self.show_key_label(self.get_key_label('MAGIC'), bg_rect)
		
		# Show potion count box always, even if 0
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

	def show_exp(self, exp):
		text_surf = self.font.render(f'EXP: {int(exp)}', False, TEXT_COLOR)
		x = self.display_surface.get_size()[0] - 240
		y = self.display_surface.get_size()[1] - 20
		text_rect = text_surf.get_rect(bottomright = (x,y))
		box_rect = text_rect.inflate(20, 10)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect, border_radius = 5)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, box_rect, 3, border_radius = 5)
		self.display_surface.blit(text_surf, text_rect)

	def draw_skill_tree(self, player, category_index, skill_index, mode, level_obj = None):
		# Draw dark overlay
		overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 220))
		self.display_surface.blit(overlay, (0, 0))

		# Main window
		window_rect = pygame.Rect(60, 60, WIDTH - 120, HEIGHT - 120)
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, window_rect, border_radius = 15)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE if mode == 'category' else UI_BORDER_COLOR, window_rect, 4, border_radius = 15)

		# Title (Small)
		title_font = pygame.font.Font(UI_FONT, 20)
		title_surf = title_font.render('CÂY KỸ NĂNG', False, 'gold')
		title_rect = title_surf.get_rect(midtop = (WIDTH // 2, 75))
		self.display_surface.blit(title_surf, title_rect)

		# EXP Display
		exp_font = pygame.font.Font(UI_FONT, 14)
		exp_surf = exp_font.render(f'EXP: {int(player.exp)}', False, '#b8ffb8')
		exp_rect = exp_surf.get_rect(topright = (window_rect.right - 30, 75))
		self.display_surface.blit(exp_surf, exp_rect)

		# Categories
		categories = player.skill_tree_categories
		cat_count = len(categories)
		cat_gap = 12
		cat_w = (window_rect.width - 60 - ((cat_count - 1) * cat_gap)) // cat_count
		cat_h = 60
		cat_y = window_rect.top + 50

		for idx, category in enumerate(categories):
			cat_rect = pygame.Rect(window_rect.left + 30 + idx * (cat_w + cat_gap), cat_y, cat_w, cat_h)
			selected = idx == category_index and mode == 'category'
			
			bg_color = '#2d4d3b' if selected else '#1a1a1a'
			pygame.draw.rect(self.display_surface, bg_color, cat_rect, border_radius = 10)
			border_color = UI_BORDER_COLOR_ACTIVE if selected else UI_BORDER_COLOR
			pygame.draw.rect(self.display_surface, border_color, cat_rect, 2, border_radius = 10)

			name_font = self.fit_font_to_width(category['name'], cat_rect.width - 16, max_size = 14, min_size = 10)
			name_surf = name_font.render(category['name'], False, TEXT_COLOR)
			self.display_surface.blit(name_surf, (cat_rect.left + 10, cat_rect.top + 10))

			opened = sum(1 for n in category['nodes'] if player.is_skill_unlocked(n['id']))
			prog_surf = self.font.render(f"{opened}/{len(category['nodes'])}", False, '#888888')
			prog_surf = pygame.transform.scale_by(prog_surf, 0.7)
			self.display_surface.blit(prog_surf, (cat_rect.right - prog_surf.get_width() - 10, cat_rect.bottom - 22))

		# Skills area with scrolling
		info_h = 90
		info_rect = pygame.Rect(window_rect.left + 30, window_rect.bottom - info_h - 20, window_rect.width - 60, info_h)
		
		scroll_area_rect = pygame.Rect(window_rect.left + 20, cat_y + cat_h + 15, window_rect.width - 40, info_rect.top - (cat_y + cat_h + 25))
		
		selected_category = player.skill_tree_categories[category_index]
		# Filter nodes: 
		# 1. Weapon check
		# 2. Prerequisites check (hide LV2 until LV1 is unlocked)
		nodes = [
			n for n in selected_category['nodes'] 
			if (n.get('weapon') is None or n.get('weapon') in player.unlocked_weapons) and
			   (all(player.is_skill_unlocked(p) for p in n.get('prereq', [])))
		]

		node_w, node_h = 280, 70
		gap_x, gap_y = 25, 15
		cols = 2
		x_start = scroll_area_rect.left + (scroll_area_rect.width - (cols * node_w + (cols-1)*gap_x)) // 2
		y_start = scroll_area_rect.top
		
		# Auto-scroll logic: ensure selected node is visible
		if mode == 'skill' and level_obj:
			row = skill_index // cols
			node_top_in_scroll = row * (node_h + gap_y)
			node_bottom_in_scroll = node_top_in_scroll + node_h
			
			if node_top_in_scroll < level_obj.skill_tree_scroll:
				level_obj.skill_tree_scroll = node_top_in_scroll
			elif node_bottom_in_scroll > level_obj.skill_tree_scroll + scroll_area_rect.height:
				level_obj.skill_tree_scroll = node_bottom_in_scroll - scroll_area_rect.height

		scroll_y = level_obj.skill_tree_scroll if level_obj else 0

		# Draw skills within clip
		self.display_surface.set_clip(scroll_area_rect)
		for idx, node in enumerate(nodes):
			col = idx % cols
			row = idx // cols
			rect = pygame.Rect(x_start + col * (node_w + gap_x), y_start + row * (node_h + gap_y) - scroll_y, node_w, node_h)
			
			if rect.bottom < scroll_area_rect.top or rect.top > scroll_area_rect.bottom:
				continue # Optimized: don't draw if outside view

			unlocked = player.is_skill_unlocked(node['id'])
			available = player.can_unlock_skill(node)
			selected_node = mode == 'skill' and idx == skill_index
			
			node_bg = '#24352f' if unlocked else '#151515'
			pygame.draw.rect(self.display_surface, node_bg, rect, border_radius = 8)
			
			b_color = UI_BORDER_COLOR_ACTIVE if selected_node else '#4ade80' if unlocked else '#60a5fa' if available else '#333333'
			b_width = 3 if selected_node else 1
			pygame.draw.rect(self.display_surface, b_color, rect, b_width, border_radius = 8)

			# Skill Name (Small)
			label_font = self.fit_font_to_width(node['name'], rect.width - 80, max_size = 13, min_size = 9)
			label_surf = label_font.render(node['name'], False, TEXT_COLOR)
			self.display_surface.blit(label_surf, (rect.left + 12, rect.top + 10))

			# Cost / Status
			st_font = pygame.font.Font(UI_FONT, 10)
			if unlocked:
				status_text, status_color = "ĐÃ MỞ", '#4ade80'
			else:
				status_text, status_color = f"GIÁ: {node['cost']}", ('gold' if player.exp >= node['cost'] else '#ff5555')
			
			status_surf = st_font.render(status_text, False, status_color)
			self.display_surface.blit(status_surf, (rect.right - status_surf.get_width() - 12, rect.top + 10))

			# Available status
			if not unlocked:
				avail_text = "SẴN SÀNG" if available else "KHÔNG ĐỦ EXP"
				avail_color = '#60a5fa' if available else '#888888'
				avail_surf = st_font.render(avail_text, False, avail_color)
				self.display_surface.blit(avail_surf, (rect.left + 12, rect.bottom - 22))

		self.display_surface.set_clip(None)

		# Info Panel at bottom
		pygame.draw.rect(self.display_surface, '#0c0c0c', info_rect, border_radius = 12)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, info_rect, 2, border_radius = 12)

		if mode == 'category':
			title_txt = f"NHÁNH: {selected_category['name'].upper()}"
			desc_txt = selected_category['desc']
			hint_txt = 'A/D: CHỌN NHÁNH | SPACE/ENTER/S: VÀO NHÁNH'
		else:
			node = nodes[skill_index] if nodes else None
			title_txt = node['name'].upper() if node else ""
			desc_txt = node['desc'] if node else ""
			hint_txt = 'SPACE: NÂNG CẤP | W/S (BIÊN): QUAY LẠI'

		title_s = self.font.render(title_txt, False, 'gold')
		title_s = pygame.transform.scale_by(title_s, 0.8)
		self.display_surface.blit(title_s, (info_rect.left + 15, info_rect.top + 12))
		
		d_font = pygame.font.Font(UI_FONT, 12)
		d_surf = d_font.render(desc_txt, False, TEXT_COLOR)
		self.display_surface.blit(d_surf, (info_rect.left + 15, info_rect.top + 38))
		
		h_font = pygame.font.Font(UI_FONT, 10)
		h_surf = h_font.render(hint_txt, False, '#888888')
		self.display_surface.blit(h_surf, (info_rect.left + 15, info_rect.bottom - 20))

	def display(self, player, map_index, monster_count, total_monsters, elapsed_time):
		self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR, player.target_health)
		self.show_armor_bar(player.armor, player.stats['armor'], self.armor_bar_rect, ARMOR_COLOR)
		self.show_monster_count(monster_count, total_monsters)
		self.show_timer(elapsed_time)
		self.show_exp(player.exp)

		self.show_map_index(map_index)

		self.weapon_overlay(player.weapon, not player.can_switch_weapon)
		self.magic_overlay(player.magic_index, not player.can_switch_magic, player)
		
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
