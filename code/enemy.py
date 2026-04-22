import pygame
import random
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, enemy_type='spirit1'):
        super().__init__(groups)
        self.enemy_type = enemy_type
        self.import_enemy_assets()
        
        # Set initial image and rect
        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, -8)
        
        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 2
        self.obstacle_sprites = obstacle_sprites
        
        # Animation
        self.status = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.1
        
        # AI behavior
        self.patrol_direction = random.choice(['horizontal', 'vertical'])
        self.patrol_timer = 0
        self.change_direction_timer = 0
        
    def import_enemy_assets(self):
        enemy_path = f'../image/cursed_spirits/{self.enemy_type}.png'
        try:
            sprite = pygame.image.load(enemy_path).convert_alpha()
            # Remove white background similar to player
            sprite = self.remove_background(sprite)
            # Scale sprite
            sprite = pygame.transform.scale_by(sprite, 0.5)
            
            # Create simple animations (just idle for now)
            self.animations = {
                'idle': [sprite],
                'move': [sprite, pygame.transform.flip(sprite, True, False)]
            }
        except:
            # Fallback to simple colored square if sprite not found
            sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
            if self.enemy_type == 'spirit1':
                pygame.draw.circle(sprite, (80, 20, 120), (16, 16), 12)
            elif self.enemy_type == 'spirit2':
                pygame.draw.ellipse(sprite, (150, 50, 50), (8, 12, 16, 8))
            else:
                pygame.draw.ellipse(sprite, (200, 200, 255), (8, 8, 16, 16))
            
            self.animations = {
                'idle': [sprite],
                'move': [sprite, pygame.transform.flip(sprite, True, False)]
            }
    
    def remove_background(self, sprite):
        """Remove white background from sprite"""
        width, height = sprite.get_size()
        stack = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
        visited = set()
        threshold = 230
        
        while stack:
            x, y = stack.pop()
            if (x, y) not in visited and 0 <= x < width and 0 <= y < height:
                visited.add((x, y))
                color = sprite.get_at((x, y))
                if color.a > 0 and color.r > threshold and color.g > threshold and color.b > threshold:
                    if abs(color.r - color.g) < 20 and abs(color.g - color.b) < 20:
                        sprite.set_at((x, y), (0, 0, 0, 0))
                        stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
        return sprite
    
    def get_status(self):
        if self.direction.magnitude() > 0:
            self.status = 'move'
        else:
            self.status = 'idle'
    
    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
    
    def ai_behavior(self):
        """Simple AI: patrol movement"""
        self.change_direction_timer += 1
        
        # Change direction periodically
        if self.change_direction_timer > 120:  # Every 2 seconds at 60 FPS
            self.change_direction_timer = 0
            if self.patrol_direction == 'horizontal':
                self.direction.x = random.choice([-1, 0, 1])
                self.direction.y = 0
            else:
                self.direction.y = random.choice([-1, 0, 1])
                self.direction.x = 0
    
    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.rect.center = self.hitbox.center
        self.collision('vertical')
    
    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                        self.direction.x = -1  # Reverse direction
                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                        self.direction.x = 1  # Reverse direction
        
        elif direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                        self.direction.y = -1  # Reverse direction
                    elif self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                        self.direction.y = 1  # Reverse direction
    
    def update(self):
        self.ai_behavior()
        self.get_status()
        self.animate()
        self.move(self.speed)
