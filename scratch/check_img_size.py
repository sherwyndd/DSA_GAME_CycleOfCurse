import pygame
import sys

pygame.init()
try:
    img = pygame.image.load('../image/sword.jpg')
    print(f"Size: {img.get_size()}")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
