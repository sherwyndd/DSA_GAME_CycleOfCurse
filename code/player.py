import pygame
import os
import math
from settings import *

class Player(pygame.sprite.Sprite):
    """
    Lớp đại diện cho nhân vật người chơi trong game.
    Quản lý di chuyển, va chạm, hoạt ảnh (animation) và các kỹ năng của nhân vật.
    """
    def __init__(self, pos, groups, obstacle_sprites, create_attack):
        """
        Khởi tạo đối tượng Player.
        
        Args:
            pos (tuple): Vị trí ban đầu của nhân vật (x, y).
            groups (list): Danh sách các nhóm sprite mà nhân vật thuộc về.
            obstacle_sprites (pygame.sprite.Group): Nhóm các sprite vật cản để kiểm tra va chạm.
        """
        super().__init__(groups)
        
        # Attribute setup
        self.obstacle_sprites = obstacle_sprites
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.is_attacking = False
        self.attack_type = None # 'attack' or 'dash'
        self.can_attack = True
        self.can_dash = True
        self.attack_time = None
        self.action_duration = 250 # Faster attack (was 400)
        self.attack_cooldown_duration = 200 # Faster cooldown (was 400)
        self.dash_cooldown_duration = 2000
        self.attack_cooldown_time = 0
        self.dash_cooldown_time = 0
        self.create_attack = create_attack
        # Character configuration
        self.char_config = {
            1: {'name': 'Monkey', 'img': 'monkey.png', 'walk': 'monkey-walk.png', 'color': (235, 202, 149)},
            2: {'name': 'Megumi', 'img': 'megumi.png', 'walk': None, 'color': (255, 230, 210)},
            3: {'name': 'Sukuna', 'img': 'sukuna.png', 'walk': None, 'color': (255, 200, 200)}
        }
        self.player_index = PLAYER_INDEX
        
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
        """
        Thuật toán Flood Fill để xóa nền ảnh một cách thông minh.
        Chỉ xóa các điểm ảnh nền kết nối với các góc, giúp giữ lại các chi tiết trắng bên trong (như mắt).

        Args:
            surf (pygame.Surface): Surface cần xử lý xóa nền.
            
        Returns:
            pygame.Surface: Surface đã được làm sạch nền.
        """
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
                if diff < 100: 
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
                    frame = pygame.transform.scale_by(frame, 0.4) 
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

        # Load character config
        config = self.char_config.get(self.player_index, self.char_config[1])
        char_path = '../image/' + config['img']
        walk_path = '../image/' + config['walk'] if config['walk'] else None

        # Load base idle sprite
        try:
            idle_surf = pygame.image.load(char_path).convert_alpha()
            idle_surf = self.remove_background_floodfill(idle_surf)
            idle_surf = pygame.transform.scale_by(idle_surf, 0.4)
        except:
            idle_surf = pygame.Surface((64,64)); idle_surf.fill('red')

        # Load walk animation if available
        if walk_path:
            walk_frames = self.slice_spritesheet(walk_path, 4, 1)
        else:
            walk_frames = [idle_surf]

        flipped_idle = pygame.transform.flip(idle_surf, True, False)
        flipped_walk = [pygame.transform.flip(f, True, False) for f in walk_frames]

        # Fill animations dictionary
        self.animations['idle'] = [idle_surf]
        self.animations['down_idle'] = [idle_surf]; self.animations['up_idle'] = [idle_surf]
        self.animations['right_idle'] = [idle_surf]; self.animations['left_idle'] = [flipped_idle]
        
        self.animations['right'] = walk_frames; self.animations['left'] = flipped_walk
        self.animations['up'] = walk_frames; self.animations['down'] = walk_frames
        
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
                self.status = self.status.split('_')[0] + '_idle'

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
            progress = (pygame.time.get_ticks() - self.attack_time) / self.action_duration
            sin_val = math.sin(progress * math.pi)
            
            if self.attack_type == 'attack':
                # Character stays still during attack as requested
                self.effect_offset = 0 
            else: # dash
                angle = sin_val * 15
                if 'left' in self.status: angle *= -1
                image = pygame.transform.rotate(image, angle)
                self.effect_offset = sin_val * 15
        else:
            self.effect_offset = 0

        self.image = image
        self.rect = self.image.get_rect(center = self.hitbox.center)

    def input(self):
        """
        Xử lý các phím nhấn từ người dùng để điều khiển nhân vật.
        - W, A, S, D: Di chuyển.
        - SPACE: Tấn công (Attack).
        - L-CTRL: Lướt nhanh (Dash).
        """
        if self.is_attacking: return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.direction.y = -1
        elif keys[pygame.K_s]: self.direction.y = 1
        else: self.direction.y = 0

        if keys[pygame.K_d]: self.direction.x = 1
        elif keys[pygame.K_a]: self.direction.x = -1
        else: self.direction.x = 0

        # SPACE = ATTACK
        if (keys[pygame.K_SPACE] and not self.is_attacking and self.can_attack):
            self.is_attacking = True
            self.attack_type = 'attack'
            self.create_attack() # Re-enabled
            self.attack_time = pygame.time.get_ticks()
            self.frame_index = 0
            self.direction.x = 0
            self.direction.y = 0
            
        # L-CTRL = DASH 
        if (keys[pygame.K_LCTRL] and not self.is_attacking and self.can_dash):
            self.is_attacking = True
            self.attack_type = 'dash'
            self.attack_time = pygame.time.get_ticks()
            self.frame_index = 0
            self.direction.x = 0
            self.direction.y = 0

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
        
        # Kiểm tra kết thúc hành động (Action duration)
        if self.is_attacking:
            if current_time - self.attack_time >= self.action_duration:
                self.is_attacking = False
                # Bắt đầu thời gian hồi chiêu sau khi hành động kết thúc
                if self.attack_type == 'attack':
                    self.can_attack = False
                    self.attack_cooldown_time = current_time
                elif self.attack_type == 'dash':
                    self.can_dash = False
                    self.dash_cooldown_time = current_time

        # Kiểm tra hồi chiêu cho Attack
        if not self.can_attack:
            if current_time - self.attack_cooldown_time >= self.attack_cooldown_duration:
                self.can_attack = True
        
        # Kiểm tra hồi chiêu cho Dash
        if not self.can_dash:
            if current_time - self.dash_cooldown_time >= self.dash_cooldown_duration:
                self.can_dash = True

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
