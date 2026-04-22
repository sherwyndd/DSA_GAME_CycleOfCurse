import pygame
import sys

# Initialize Pygame
pygame.init()

# Create cursed spirit sprites
def create_spirit1():
    """Create a simple cursed spirit - floating orb with eyes"""
    surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    # Main body - dark purple orb
    pygame.draw.circle(surface, (80, 20, 120), (32, 32), 25)
    pygame.draw.circle(surface, (100, 30, 140), (32, 32), 22)
    
    # Evil eyes
    pygame.draw.ellipse(surface, (255, 255, 255), (20, 25, 8, 12))
    pygame.draw.ellipse(surface, (255, 255, 255), (36, 25, 8, 12))
    pygame.draw.circle(surface, (0, 0, 0), (24, 30), 3)
    pygame.draw.circle(surface, (0, 0, 0), (40, 30), 3)
    
    # Evil grin
    pygame.draw.arc(surface, (0, 0, 0), (22, 35, 20, 15), 0, 3.14, 3)
    
    return surface

def create_spirit2():
    """Create a worm-like cursed spirit"""
    surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    # Worm body segments
    pygame.draw.ellipse(surface, (150, 50, 50), (10, 20, 15, 25))
    pygame.draw.ellipse(surface, (180, 60, 60), (22, 18, 15, 28))
    pygame.draw.ellipse(surface, (150, 50, 50), (34, 16, 15, 30))
    pygame.draw.ellipse(surface, (120, 40, 40), (46, 18, 12, 25))
    
    # Eyes
    pygame.draw.circle(surface, (255, 0, 0), (28, 25), 3)
    pygame.draw.circle(surface, (255, 0, 0), (38, 23), 3)
    
    return surface

def create_spirit3():
    """Create a ghost-like cursed spirit"""
    surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    # Ghost body
    pygame.draw.ellipse(surface, (200, 200, 255), (15, 15, 34, 40))
    pygame.draw.polygon(surface, (200, 200, 255), [(15, 45), (20, 55), (25, 48), (30, 55), (35, 48), (40, 55), (45, 48), (49, 55), (49, 45)])
    
    # Evil eyes
    pygame.draw.ellipse(surface, (0, 0, 0), (22, 25, 6, 8))
    pygame.draw.ellipse(surface, (0, 0, 0), (36, 25, 6, 8))
    
    # Mouth
    pygame.draw.arc(surface, (0, 0, 0), (25, 35, 14, 10), 0, 3.14, 2)
    
    return surface

# Create and save the sprites
spirit1 = create_spirit1()
spirit2 = create_spirit2()
spirit3 = create_spirit3()

pygame.image.save(spirit1, "image/cursed_spirits/spirit1.png")
pygame.image.save(spirit2, "image/cursed_spirits/spirit2.png")
pygame.image.save(spirit3, "image/cursed_spirits/spirit3.png")

print("Cursed spirit sprites created successfully!")
pygame.quit()
