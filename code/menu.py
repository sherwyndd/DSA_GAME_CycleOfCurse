import pygame
from settings import *

class Menu:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, 30)
        self.sub_font = pygame.font.Font(UI_FONT, 20)
        
        # Background - Sleek Black
        self.bg_color = '#050505'
            
        # Selection
        self.selection_index = 0
        self.buttons = ['PLAY GAME', 'SETTINGS', 'LEADERBOARD', 'EXIT']
        
    def display(self):
        self.display_surface.fill(self.bg_color)
        
        # Title
        title_surf = self.font.render('Game : Cycle of Curse', False, 'gold')
        title_rect = title_surf.get_rect(center = (WIDTH // 2, HEIGHT // 6))
        
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, title_rect.inflate(60,30), border_radius=15)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, title_rect.inflate(60,30), 4, border_radius=15)
        self.display_surface.blit(title_surf, title_rect)
        
        # Buttons
        for i, button in enumerate(self.buttons):
            is_selected = i == self.selection_index
            color = UI_BORDER_COLOR_ACTIVE if is_selected else TEXT_COLOR
            
            # Button Box
            btn_width = 350
            btn_height = 50
            rect = pygame.Rect(0, 0, btn_width, btn_height)
            rect.center = (WIDTH // 2, HEIGHT // 2 - 50 + i * 80)
            
            # Draw button background
            bg_color = '#1a1a1a' if is_selected else UI_BG_COLOR
            pygame.draw.rect(self.display_surface, bg_color, rect, border_radius = 8)
            
            # Draw border
            border_color = UI_BORDER_COLOR_ACTIVE if is_selected else UI_BORDER_COLOR
            border_width = 4 if is_selected else 2
            pygame.draw.rect(self.display_surface, border_color, rect, border_width, border_radius = 8)
            
            # Text
            surf = self.font.render(button, False, color)
            text_rect = surf.get_rect(center = rect.center)
            
            # Pulsing effect for selected button
            if is_selected:
                import math
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
                glow_color = (int(255 * pulse), int(215 * pulse), 0)
                pygame.draw.rect(self.display_surface, glow_color, rect.inflate(4,4), 2, border_radius = 10)
            
            self.display_surface.blit(surf, text_rect)

class Settings:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, 20)
        self.title_font = pygame.font.Font(UI_FONT, 30)
        
        self.actions = list(CONTROLS.keys())
        self.selection_index = 0
        self.waiting_for_key = False
        
    def display(self):
        self.display_surface.fill('#050505')
        
        title_surf = self.title_font.render('SETTINGS', False, 'gold')
        title_rect = title_surf.get_rect(center = (WIDTH // 2, 80))
        self.display_surface.blit(title_surf, title_rect)
        
        # Header
        h_action = self.font.render('ACTION', False, 'gray')
        h_key = self.font.render('BINDING', False, 'gray')
        self.display_surface.blit(h_action, (WIDTH // 2 - 250, 150))
        self.display_surface.blit(h_key, (WIDTH // 2 + 50, 150))
        pygame.draw.line(self.display_surface, UI_BORDER_COLOR_ACTIVE, (WIDTH // 2 - 270, 180), (WIDTH // 2 + 250, 180), 2)

        for i, action in enumerate(self.actions):
            is_selected = i == self.selection_index
            y = 220 + i * 50
            
            # Highlight box
            if is_selected:
                box_rect = pygame.Rect(WIDTH // 2 - 270, y - 10, 540, 40)
                color = '#222222' if not self.waiting_for_key else '#331111'
                pygame.draw.rect(self.display_surface, color, box_rect, border_radius=5)
                pygame.draw.rect(self.display_surface, 'gold', box_rect, 2, border_radius=5)
            
            # Action Name
            action_surf = self.font.render(action, False, TEXT_COLOR)
            self.display_surface.blit(action_surf, (WIDTH // 2 - 250, y))
            
            # Key Binding
            key_val = CONTROLS[action]
            if is_selected and self.waiting_for_key:
                key_text = 'PRESS ANY KEY...'
                color = 'gold'
            elif key_val is None:
                key_text = 'NONE'
                color = 'red'
            else:
                key_text = pygame.key.name(key_val).upper()
                color = 'white'
            
            key_surf = self.font.render(key_text, False, color)
            self.display_surface.blit(key_surf, (WIDTH // 2 + 50, y))
            
        # Footer
        footer_text = 'SPACE: CHANGE | ESC: BACK'
        footer_surf = self.font.render(footer_text, False, 'gray')
        footer_rect = footer_surf.get_rect(center = (WIDTH // 2, HEIGHT - 50))
        self.display_surface.blit(footer_surf, footer_rect)

    def handle_input(self, event):
        if not self.waiting_for_key:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selection_index = (self.selection_index - 1) % len(self.actions)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selection_index = (self.selection_index + 1) % len(self.actions)
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    CONTROLS[self.actions[self.selection_index]] = None
                    self.waiting_for_key = True
                elif event.key == pygame.K_ESCAPE:
                    return 'MENU'
        else:
            if event.type == pygame.KEYDOWN:
                # Check for conflicts
                new_key = event.key
                for action in self.actions:
                    if CONTROLS[action] == new_key:
                        CONTROLS[action] = None
                
                # Assign new key
                CONTROLS[self.actions[self.selection_index]] = new_key
                self.waiting_for_key = False
        return 'SETTINGS'

class Leaderboard:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, 20)
        self.title_font = pygame.font.Font(UI_FONT, 30)
        self.bg_color = UI_BG_COLOR
        
    def get_data(self):
        import json
        import os
        if not os.path.exists('leaderboard.json'):
            return []
        try:
            with open('leaderboard.json', 'r') as f:
                return json.load(f)
        except:
            return []

    def save_record(self, round_name, time_sec):
        import json
        import os
        data = self.get_data()
        data.append({'round': round_name, 'time': time_sec})
        
        # Sort: Win > Round 3 > 2 only (Round 1 not ranked)
        def sort_key(entry):
            r = entry['round']
            priority = 0
            if r == 'Win': priority = 5
            elif 'Round 3' in r: priority = 4
            elif 'Round 2' in r: priority = 3
            
            # Shorter time is better (negative so larger is better for reverse sort)
            return (priority, -entry['time'])
            
        data.sort(key=sort_key, reverse=True)
        data = data[:10] # Keep top 10
        
        with open('leaderboard.json', 'w') as f:
            json.dump(data, f)

    def display(self):
        self.display_surface.fill(self.bg_color)
        
        title_surf = self.title_font.render('LEADERBOARD', False, 'gold')
        title_rect = title_surf.get_rect(center = (WIDTH // 2, 80))
        self.display_surface.blit(title_surf, title_rect)
        
        data = self.get_data()
        
        # Headers
        h_round = self.font.render('RANK   ROUND', False, TEXT_COLOR)
        h_time = self.font.render('TIME', False, TEXT_COLOR)
        self.display_surface.blit(h_round, (WIDTH // 2 - 200, 150))
        self.display_surface.blit(h_time, (WIDTH // 2 + 100, 150))
        pygame.draw.line(self.display_surface, UI_BORDER_COLOR_ACTIVE, (WIDTH // 2 - 220, 180), (WIDTH // 2 + 200, 180), 2)
        
        for i, entry in enumerate(data):
            y = 210 + i * 40
            rank_surf = self.font.render(f'{i+1:2d}.', False, 'gold')
            round_surf = self.font.render(entry['round'], False, TEXT_COLOR)
            
            minutes = entry['time'] // 60
            seconds = entry['time'] % 60
            time_str = f'{minutes:02d}:{seconds:02d}'
            time_surf = self.font.render(time_str, False, TEXT_COLOR)
            
            self.display_surface.blit(rank_surf, (WIDTH // 2 - 210, y))
            self.display_surface.blit(round_surf, (WIDTH // 2 - 140, y))
            self.display_surface.blit(time_surf, (WIDTH // 2 + 100, y))
            
        back_surf = self.font.render('PRESS ESC TO BACK', False, 'gray')
        back_rect = back_surf.get_rect(center = (WIDTH // 2, HEIGHT - 50))
        self.display_surface.blit(back_surf, back_rect)
