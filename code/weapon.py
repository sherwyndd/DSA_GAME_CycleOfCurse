import pygame
import math

class Weapon(pygame.sprite.Sprite):
    # Class-level cache to avoid processing the image every time an attack is made
    cached_sword_image = None

    def remove_background_floodfill(self, surf):
        """
        Xóa nền bắt đầu từ các góc lan vào trong, dừng lại khi chạm vật thể.
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
                if diff < 70: 
                    surf.set_at((x, y), (0, 0, 0, 0))
                    stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
        return surf

    def __init__(self, player, groups):
        super().__init__(groups)
        self.player = player
        self.direction = player.status.split('_')[0]
        
        # Load sword image
        if Weapon.cached_sword_image is None:
            try:
                import os
                base_path = os.path.dirname(__file__)
                full_path = os.path.join(base_path, '../image/sword.jpg')
                
                temp_image = pygame.image.load(full_path).convert_alpha()
                # Sử dụng Flood Fill để xóa nền thông minh
                temp_image = self.remove_background_floodfill(temp_image)
                
                # Scale về kích thước 0.3 như ban đầu
                Weapon.cached_sword_image = pygame.transform.scale_by(temp_image, 0.3)
            except Exception as e:
                print(f"Lỗi nạp ảnh kiếm: {e}")
                Weapon.cached_sword_image = pygame.Surface((10, 50), pygame.SRCALPHA)
                Weapon.cached_sword_image.fill((200, 200, 200))

        self.original_image = Weapon.cached_sword_image



        self.image = self.original_image

        # Positioning and Animation
        self.start_time = pygame.time.get_ticks()
        self.duration = player.action_duration
        
        # Swapped left and right based on feedback
        if self.direction == 'right': self.angle = 0
        elif self.direction == 'left': self.angle = 180
        elif self.direction == 'up': self.angle = 90
        else: self.angle = -90 # down

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.update_position()

    def update_position(self):
        # Progress from 0 to 1
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration
        if progress > 1: progress = 1
        
        # Thrust animation: Sin wave for extension (out and back)
        sin_val = math.sin(progress * math.pi)
        # Reduced offset to make it "lower/closer" to the character
        thrust_offset = 18 + sin_val * 30
        
        # Calculate position based on direction
        rad = 0
        if self.direction == 'right': rad = 0
        elif self.direction == 'left': rad = math.pi
        elif self.direction == 'up': rad = -math.pi/2
        elif self.direction == 'down': rad = math.pi/2
        
        # Adjust center position
        cx = self.player.rect.centerx + math.cos(rad) * thrust_offset
        cy = self.player.rect.centery + math.sin(rad) * thrust_offset 
        
        self.rect = self.image.get_rect(center = (cx, cy))
        self.hitbox = self.rect

    def update(self):
        self.update_position()
        if pygame.time.get_ticks() - self.start_time >= self.duration:
            self.kill()