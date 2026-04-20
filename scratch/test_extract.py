import pygame
import os

def extract_tiles():
    pygame.init()
    img = pygame.image.load('image/background.png')
    w, h = img.get_size()
    
    # Assuming 24 cols and 14 rows as per settings.py
    cols = 24
    rows = 14
    
    tw = w / cols
    th = h / rows
    
    print(f"Image size: {w}x{h}")
    print(f"Tile size: {tw}x{th}")
    
    # Create directory for output if needed, or just print info
    # I'll just save a few samples to check
    try:
        os.makedirs('scratch/tiles', exist_ok=True)
    except:
        pass
        
    # Sample 1: Fence (0,0)
    fence = img.subsurface((0, 0, int(tw), int(th)))
    pygame.image.save(fence, 'scratch/tiles/fence.png')
    
    # Sample 2: Floor (1,1)
    floor1 = img.subsurface((int(tw), int(th), int(tw), int(th)))
    pygame.image.save(floor1, 'scratch/tiles/floor1.png')
    
    # Sample 3: Torch (at (7,0))
    torch = img.subsurface((int(7*tw), 0, int(tw), int(th)))
    pygame.image.save(torch, 'scratch/tiles/torch.png')
    
    # Sample 4: Floor with grate (looked like it was around (5,2) maybe?)
    # Looking at the image again:
    # Grates at (6,2), (14,1), (5,4) approx...
    floor_grate = img.subsurface((int(6*tw), int(2*th), int(tw), int(th)))
    pygame.image.save(floor_grate, 'scratch/tiles/floor_grate.png')

if __name__ == "__main__":
    extract_tiles()
