import pygame
import os
import math
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        
        # Attribute setup
        self.obstacle_sprites = obstacle_sprites
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.is_attacking = False
        self.attack_type = None # 'attack' or 'dash'
        self.attack_cooldown = 400
        self.attack_time = None
        
        # Animation setup
        self.import_player_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        self.animation_speed = 0.15
        
        # Initial image
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -8)

        # Visual effect offset
        self.effect_offset = 0

    def remove_background_floodfill(self, surf):
        width, height = surf.get_size()
        stack = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
        visited = set()
        bg_color = surf.get_at((0,0))
        
        while stack:
            x, y = stack.pop()
            if (x, y) not in visited and 0 <= x < width and 0 <= y < height:
                visited.add((x, y))
                color = surf.get_at((x, y))
                diff = sum(abs(color[i]-bg_color[i]) for i in range(3))
                if diff < 60:
                    surf.set_at((x, y), (0, 0, 0, 0))
                    stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
        return surf

    def slice_spritesheet(self, path, cols, rows):
        try:
            sheet = pygame.image.load(path).convert_alpha()
            sheet = self.remove_background_floodfill(sheet)
            w = sheet.get_width() // cols
            h = sheet.get_height() // rows
            frames = []
            for r in range(rows):
                for c in range(cols):
                    rect = pygame.Rect(c * w, r * h, w, h)
                    frame = sheet.subsurface(rect).copy()
                    frame = pygame.transform.scale_by(frame, 1/2.5)
                    frames.append(frame)
            return frames
        except:
            return []

    def import_player_assets(self):
        self.animations = {
            'idle': [], 'up': [], 'down': [], 'left': [], 'right': [], 
            'right_idle' :[], 'left_idle' :[], 'up_idle' :[], 'down_idle' :[], 
            'attack': [], 'dash': [] 
        }

        # Load base monkies
        try:
            idle_surf = pygame.image.load('../image/monkey.png').convert_alpha()
            idle_surf = self.remove_background_floodfill(idle_surf)
            idle_surf = pygame.transform.scale_by(idle_surf, 1/2.5)
        except:
            idle_surf = pygame.Surface((64,64))
            idle_surf.fill('red')

        walk_frames = self.slice_spritesheet('../image/monkey-walk.png', 4, 1)
        if not walk_frames: walk_frames = [idle_surf]

        flipped_idle = pygame.transform.flip(idle_surf, True, False)
        flipped_walk = [pygame.transform.flip(f, True, False) for f in walk_frames]

        # Fill animations dictionary
        self.animations['idle'] = [idle_surf]
        self.animations['down_idle'] = [idle_surf]
        self.animations['up_idle'] = [idle_surf]
        self.animations['right_idle'] = [idle_surf]
        self.animations['left_idle'] = [flipped_idle]
        
        self.animations['right'] = walk_frames
        self.animations['left'] = flipped_walk
        self.animations['up'] = walk_frames 
        self.animations['down'] = walk_frames
        
        self.animations['attack'] = [idle_surf] 
        self.animations['dash'] = [idle_surf]

    def get_status(self):
        if self.is_attacking:
            if '_attack' not in self.status and '_dash' not in self.status:
                self.status = self.status.split('_')[0] + '_' + self.attack_type
            return

        if self.direction.x == 1: self.status = 'right'
        elif self.direction.x == -1: self.status = 'left'
        elif self.direction.y == -1: self.status = 'up'
        elif self.direction.y == 1: self.status = 'down'
        else:
            if 'idle' not in self.status:
                self.status += '_idle'

    def animate(self):
        base_status = self.status.split('_')[0]
        if base_status in ['attack', 'dash']: base_status = 'down'
        
        animation = self.animations.get(self.status, self.animations.get(base_status, self.animations['idle']))
        if not animation: animation = [pygame.Surface((32,32))]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)].copy()
        
        if self.is_attacking:
            progress = (pygame.time.get_ticks() - self.attack_time) / self.attack_cooldown
            sin_val = math.sin(progress * math.pi)
            
            if self.attack_type == 'attack':
                # Lean 10 degrees down/forward
                angle = sin_val * 10
                if 'left' in self.status: angle *= -1
                
                # DRAW ARM LOWERED
                arm_color = (255, 220, 180)
                arm_w, arm_h = 10, 5
                arm_x = image.get_width() * 0.7
                arm_y = image.get_height() * 0.65 # Lowered arm position
                if 'left' in self.status: arm_x = image.get_width() * 0.3 - arm_w
                
                pygame.draw.rect(image, arm_color, (arm_x, arm_y, arm_w, arm_h))
                
                image = pygame.transform.rotate(image, angle)
                self.effect_offset = sin_val * 3 
            else: # dash (L-CTRL)
                angle = sin_val * 15 # Tilt
                if 'left' in self.status: angle *= -1
                image = pygame.transform.rotate(image, angle)
                self.effect_offset = sin_val * 7 # Dash distance reduced by half (was 15)
        else:
            self.effect_offset = 0

        self.image = image
        self.rect = self.image.get_rect(center = self.hitbox.center)

    def input(self):
        if self.is_attacking: return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.direction.y = -1
        elif keys[pygame.K_s]: self.direction.y = 1
        else: self.direction.y = 0

        if keys[pygame.K_d]: self.direction.x = 1
        elif keys[pygame.K_a]: self.direction.x = -1
        else: self.direction.x = 0

        # SPACE = ATTACK
        if (keys[pygame.K_SPACE] and not self.is_attacking):
            self.is_attacking = True
            self.attack_type = 'attack'
            self.attack_time = pygame.time.get_ticks()
            self.frame_index = 0
            
        # L-CTRL = DASH 
        if (keys[pygame.K_LCTRL] and not self.is_attacking):
            self.is_attacking = True
            self.attack_type = 'dash'
            self.attack_time = pygame.time.get_ticks()
            self.frame_index = 0

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        
        lunge_vector = pygame.math.Vector2(0,0)
        if self.is_attacking:
            if 'left' in self.status: lunge_vector.x = -self.effect_offset
            elif 'right' in self.status: lunge_vector.x = self.effect_offset
            elif 'up' in self.status: lunge_vector.y = -self.effect_offset
            elif 'down' in self.status: lunge_vector.y = self.effect_offset

        self.hitbox.x += (self.direction.x * speed) + lunge_vector.x
        self.collision("horizontal")
        self.hitbox.y += (self.direction.y * speed) + lunge_vector.y
        self.collision("vertical")
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if (direction == "horizontal"):
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if (self.direction.x > 0 or 'right' in self.status): 
                        self.hitbox.right = sprite.hitbox.left
                    if (self.direction.x < 0 or 'left' in self.status): 
                        self.hitbox.left = sprite.hitbox.right
        if (direction == "vertical"):
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if (self.direction.y > 0 or 'down' in self.status):
                        self.hitbox.bottom = sprite.hitbox.top
                    if (self.direction.y < 0 or 'up' in self.status):
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if (self.is_attacking):
            if (current_time - self.attack_time >= self.attack_cooldown):
                self.is_attacking = False

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
