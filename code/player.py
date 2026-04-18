import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        # Load the monkey image and set the purple background to transparent
        # Load and resize the monkey image
        full_size_image = pygame.image.load('../image/monkey.png').convert()
        full_size_image.set_colorkey((34, 33, 49))
        self.image = pygame.transform.scale_by(full_size_image, 1/2.5) 
        self.rect = self.image.get_rect(topleft = pos)

        # Movement setup
        self.direction = pygame.math.Vector2()
        self.speed = 5

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

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * speed
        self.rect.y += self.direction.y * speed

    def update(self):
        self.input()
        self.move(self.speed)
