from os import walk
import pygame

def import_folder(path):
	"""
	Nạp toàn bộ ảnh trong một thư mục và trả về danh sách Surface.
	Sử dụng sorted() để đảm bảo thứ tự frame cho hoạt ảnh.
	"""

	surface_list = []

	for _,__,img_files in walk(path):
		for image in sorted(img_files):
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list

def remove_background_floodfill(surf, threshold = 15):
	"""
	Thuật toán Flood Fill (loang màu) để xóa nền ảnh nhân vật.
	1. Nhận diện màu nền từ 4 góc ảnh.
	2. Loang từ các biên để chuyển các vùng màu nền sang trong suốt (alpha = 0).
	3. Giữ lại màu sắc bên trong nhân vật (như mắt trắng) không bị xóa nhầm.
	"""

	width, height = surf.get_size()
	# Check corners for background color
	bg_color = surf.get_at((0,0))
	
	# If the corner is already transparent, we might not need to do anything
	if bg_color[3] == 0:
		# Try to find a non-transparent corner
		for pos in [(width-1, 0), (0, height-1), (width-1, height-1)]:
			color = surf.get_at(pos)
			if color[3] > 0:
				bg_color = color
				break
	
	if bg_color[3] == 0: return surf # Already transparent background

	stack = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
	visited = set()
	
	while stack:
		x, y = stack.pop()
		if (x, y) not in visited and 0 <= x < width and 0 <= y < height:
			visited.add((x, y))
			color = surf.get_at((x, y))
			
			# Distance in RGB space
			diff = sum(abs(color[i]-bg_color[i]) for i in range(3))
			
			if diff < threshold: 
				surf.set_at((x, y), (0, 0, 0, 0))
				stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
	return surf
