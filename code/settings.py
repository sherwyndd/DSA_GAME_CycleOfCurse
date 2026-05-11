import pygame
# game setup
WIDTH    = 900
HEIGHT   = 700
FPS      = 60
COLS     = 24
ROWS     = 16
T_WIDTH  = 1224 // COLS 
T_HEIGHT = 711 // ROWS 

# player configuration
# PLAYER_INDEX: 1=Monkey, 2=Megumi, 3=Sukuna
PLAYER_INDEX = 1
# WEAPON_INDEX: 0=Sword, 1=Lance, 2=Axe, 3=Rapier, 4=Sai
WEAPON_INDEX = 0

# ui 
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ARMOR_BAR_WIDTH = 200
MONSTER_BAR_WIDTH = 300
ITEM_BOX_SIZE = 80
UI_FONT = '../graphics/font/joystix.ttf'
UI_FONT_SIZE = 18

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# ui colors
HEALTH_COLOR = 'red'
ARMOR_COLOR = '#888888' # Gray
MONSTER_COLOR = '#8e44ad' # Purple
UI_BORDER_COLOR_ACTIVE = 'gold'

weapon_data = {
	'sword': {'cooldown': 100, 'damage': 15,'graphic':'../graphics/weapons/sword/full.png'},
	'lance': {'cooldown': 400, 'damage': 30,'graphic':'../graphics/weapons/lance/full.png'},
	'axe': {'cooldown': 300, 'damage': 20, 'graphic':'../graphics/weapons/axe/full.png'},
	'rapier':{'cooldown': 50, 'damage': 8, 'graphic':'../graphics/weapons/rapier/full.png'},
	'sai':{'cooldown': 80, 'damage': 10, 'graphic':'../graphics/weapons/sai/full.png'}}

# magic
magic_data = {
	'heal' : {'strength': 20,'cost': 0,'graphic':'../graphics/potion.png'},
	'dismantle': {'strength': 15, 'cost': 15, 'graphic': '../graphics/weapons/sai/full.png'} # Using sai graphic as placeholder
}

# map setup
# WORLD_MAP_1: Gate on Right
WORLD_MAP_1 = [
	['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','h',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','h','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','p',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x','x'],
	['x','x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
]

# WORLD_MAP_2: Gate on Left and Right
WORLD_MAP_2 = [
	['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','h',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','h','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x','x'],
	['x','x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
]

# WORLD_MAP_3: Gate on Left
WORLD_MAP_3 = [
	['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','h',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','h','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x','x'],
	['x','x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','x'],
	['x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x','x'],
]

# enemy
monster_data = {
	'spirit': {'health': 100,'damage':8,'attack_type': 'none', 'speed': 2, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 350},
	'slime': {'health': 100,'damage':8,'attack_type': 'none', 'speed': 2, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 350},
	'skeleton': {'health': 120,'damage':10,'attack_type': 'slash', 'speed': 2, 'resistance': 2, 'attack_radius': 80, 'notice_radius': 350},
	'skeleton-big': {'health': 250,'damage':15,'attack_type': 'claw', 'speed': 1.5, 'resistance': 3, 'attack_radius': 110, 'notice_radius': 350},
	'skeleton-shaman': {'health': 100,'damage':12,'attack_type': 'flame', 'speed': 0.5, 'resistance': 1, 'attack_radius': 250, 'notice_radius': 350},
	'boss': {'health': 500,'damage':25,'attack_type': 'axe', 'speed': 1.5, 'resistance': 0.1, 'attack_radius': 70, 'notice_radius': 400},
	'boss2': {'health': 600,'damage':10,'attack_type': 'sai', 'speed': 2.4, 'resistance': 0.1, 'attack_radius': 70, 'notice_radius': 400},
	'boss3': {'health': 700,'damage':30,'attack_type': 'lance', 'speed': 2.2, 'resistance': 0.1, 'attack_radius': 80, 'notice_radius': 400},
	'bull': {'health': 150,'damage':20,'attack_type': 'bull', 'speed': 2.5, 'resistance': 0, 'attack_radius': 200, 'notice_radius': 400},
	'frog': {'health': 60,'damage':2,'attack_type': 'frog', 'speed': 1.0, 'resistance': 2, 'attack_radius': 80, 'notice_radius': 400}
}


# controls
CONTROLS = {
    'UP': pygame.K_w,
    'DOWN': pygame.K_s,
    'LEFT': pygame.K_a,
    'RIGHT': pygame.K_d,
    'ATTACK': pygame.K_SPACE,
    'MAGIC': pygame.K_z,
    'SWITCH': pygame.K_q,
    'DASH': pygame.K_n
}

MAPS = {
    'first': {
        'index': 1,
        'layout': WORLD_MAP_1,
        'bg': '../graphics/background-frost.jpg',
        'width': 1224,
        'height': 711,
        'gates': [(7, 23), (8, 23), (9, 23)]
    },
    'second': {
        'index': 2,
        'layout': WORLD_MAP_2,
        'bg': '../graphics/background.png',
        'width': 1224,
        'height': 711,
        'gates': [(7, 0), (8, 0), (9, 0), (7, 23), (8, 23), (9, 23)]
    },
    'third': {
        'index': 3,
        'layout': WORLD_MAP_2,
        'bg': '../graphics/background4.png',
        'width': 1224,
        'height': 711,
        'gates': [(7, 0), (8, 0), (9, 0), (7, 23), (8, 23), (9, 23)]
    },
    'fourth': {
        'index': 4,
        'layout': WORLD_MAP_3,
        'bg': '../graphics/mahoraga-background.jpg',
        'width': 1224,
        'height': 711,
        'gates': [(7, 0), (8, 0), (9, 0)]
    }
}