import pygame
import os

pygame.init()
pygame.display.set_mode((1,1))

paths = [
    'graphics/weapons/sword/right.png',
    'graphics/weapons/sword/left.png',
    'graphics/weapons/sword/up.png',
    'graphics/weapons/sword/down.png'
]

for p in paths:
    if os.path.exists(p):
        surf = pygame.image.load(p)
        print(f"File: {p}")
        print(f"  Size: {surf.get_size()}")
        print(f"  Flags: {surf.get_flags()}")
        print(f"  Has Alpha: {surf.get_masks()[3] != 0}")
        # Check corners for common background colors
        corners = [surf.get_at((0,0)), surf.get_at((surf.get_width()-1, 0))]
        print(f"  Corners: {corners}")
    else:
        print(f"File not found: {p}")

pygame.quit()
