import pygame
import sys
import os

# Initialize Pygame
pygame.init()
pygame.display.set_mode((1, 1))  # Set minimal video mode

# Load the monkey walk sprite sheet
sprite_sheet = pygame.image.load('image/monkey-walk.png').convert_alpha()

# Remove background from sprite sheet
def remove_background(image):
    width, height = image.get_size()
    stack = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    # Add edge points for better coverage
    for x in range(width):
        stack.extend([(x, 0), (x, height - 1)])
    for y in range(height):
        stack.extend([(0, y), (width - 1, y)])
    
    visited = set()
    
    while stack:
        x, y = stack.pop()
        if (x, y) not in visited and 0 <= x < width and 0 <= y < height:
            visited.add((x, y))
            color = image.get_at((x, y))
            # Remove pure white and purple pixels
            if color.a > 0 and (
                (color.r == 255 and color.g == 255 and color.b == 255) or  # Pure white
                (color.r > 150 and color.g < 100 and color.b > 150)  # Purple background
            ):
                image.set_at((x, y), (0, 0, 0, 0))
                stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    return image

# Remove background
sprite_sheet = remove_background(sprite_sheet)

# Get sprite sheet dimensions
sheet_width, sheet_height = sprite_sheet.get_size()
print(f"Sprite sheet size: {sheet_width} x {sheet_height}")

# Estimate frame size based on visual inspection
# The monkey appears to be arranged in a grid
frame_width = sheet_width // 4  # Assuming 4 frames per row
frame_height = sheet_height // 2  # Assuming 2 rows

print(f"Estimated frame size: {frame_width} x {frame_height}")

# Extract frames and save them
frame_count = 0
for row in range(2):
    for col in range(4):
        # Calculate frame position
        x = col * frame_width
        y = row * frame_height
        
        # Extract frame
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sprite_sheet, (0, 0), pygame.Rect(x, y, frame_width, frame_height))
        
        # Scale frame
        frame = pygame.transform.scale_by(frame, 0.3)
        
        # Save frame
        frame_filename = f'image/character/player/walk/frame_{frame_count}.png'
        pygame.image.save(frame, frame_filename)
        print(f"Saved frame {frame_count}: {frame_filename}")
        frame_count += 1

print(f"Extracted {frame_count} frames")
pygame.quit()
