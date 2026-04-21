import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        # Load the monkey image and set the purple background to transparent
        # Load and resize the monkey image
        full_size_image = pygame.image.load('../image/monkey.png').convert()
        full_size_image.set_colorkey((34, 33, 49))
        self.image = pygame.transform.scale_by(full_size_image, 1/2.5) 
        self.rect = self.image.get_rect(topleft = pos)
        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.inflate(0, -8)
        self.attack_cooldown = 400
        self.attack_time = None
        # Movement setup
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.is_attacking = False
    def import_player_assets(self):
        character_path = '../image/character/player/'
        self.animations = {'idle': [], 'up': [], 'down': [], 'left': [], 'right': [], 'right_idle' :[], 'left_idle' :[], 'up_idle' :[], 'down_idle' :[], 'attack': [], 'magic': []}
    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0
        if (keys[pygame.K_SPACE] and not self.is_attacking):
            print("attack")
            self.is_attacking = True
            self.attack_time = pygame.time.get_ticks()
        if (keys[pygame.K_LCTRL] and not self.is_attacking):
            print("magic")
            self.is_attacking = True
            self.attack_time = pygame.time.get_ticks()
    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.hitbox.x += self.direction.x * speed
        self.collision("horizontal")
        self.hitbox.y += self.direction.y * speed
        self.rect.center = self.hitbox.center
        self.collision("vertical")
    def collision(self, direction):
        if (direction == "horizontal"):
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if (self.direction.x > 0): # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if (self.direction.x < 0): # moving left
                        self.hitbox.left = sprite.hitbox.right
        if (direction == "vertical"):
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if (self.direction.y > 0): # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if (self.direction.y < 0): # moving up
                        self.hitbox.top = sprite.hitbox.bottom
    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if (self.is_attacking):
            if (current_time - self.attack_time >= self.attack_cooldown):
                self.is_attacking = False
    def update(self):
        self.input()
        self.cooldowns()
        self.move(self.speed)
