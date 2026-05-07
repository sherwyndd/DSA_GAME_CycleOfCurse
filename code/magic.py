import pygame
from settings import *
from random import randint

class MagicPlayer:
	def __init__(self,animation_player):
		self.animation_player = animation_player

	def heal(self,player,strength,cost,groups):
		if player.energy >= cost:
			player.target_health += strength
			player.energy -= cost
			if player.target_health >= player.stats['health']:
				player.target_health = player.stats['health']
			
			# We could add particles here, but for now we'll just heal
			# self.animation_player.create_particles('heal',player.rect.center,groups)
