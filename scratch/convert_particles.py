import pygame
import os

def process_images():
    pygame.init()
    # Process multiple categories
    categories = {
        'thunder': (r'C:\Users\HP\Documents\DSA-Game-Project\12 - particles\12 - particles\graphics\particles\thunder', 8),
        'bamboo': (r'C:\Users\HP\Documents\DSA-Game-Project\12 - particles\12 - particles\graphics\particles\bamboo', 2)
    }

    for cat_name, (source_dir, count) in categories.items():
        target_dir = os.path.join(r'c:\Users\HP\Documents\DSA-Game-Project\graphics\particles', cat_name)
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"Created directory: {target_dir}")

        for i in range(count):
            filename = f'{i}.png'
            path = os.path.join(source_dir, filename)
            if os.path.exists(path):
                surf = pygame.image.load(path)
                new_surf = surf.copy()
                width, height = surf.get_size()
                for x in range(width):
                    for y in range(height):
                        r, g, b, a = surf.get_at((x, y))
                        if a > 0:
                            if cat_name == 'thunder':
                                # Original swap for thunder
                                new_surf.set_at((x, y), (b, g, r, a))
                            else:
                                # Bright Ice Blue for bamboo
                                new_r = min(255, int(r * 0.3) + 120)
                                new_g = min(255, int(g * 0.8) + 150)
                                new_b = 255
                                new_surf.set_at((x, y), (new_r, new_g, new_b, a))
                
                save_path = os.path.join(target_dir, filename)
                pygame.image.save(new_surf, save_path)
                print(f"Saved: {save_path}")

if __name__ == "__main__":
    process_images()
