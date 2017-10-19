import numpy as np
import random

random.seed(0)

class Agent():

	def __init__(self, num, coords, energy=1.0):
		self.num = num
		self.coords = coords
		self.energy = energy

	def __repr__(self):
		return "Agent({}, {}, energy={})".format(self.num, self.coords, self.energy)

	def __str__(self):
		return "Agent: #{} , @{} , &{}".format(self.num, self.coords, self.energy)

	def __add__(self, other):
		"""reproduction dunder"""
		return Agent(len(agents), self.coords, self.energy*other.energy)

if __name__ == "__main__":
	agents = []
	for i in range(10):
		agents.append(Agent(i, (random.randint(0, 16), random.randint(0, 16))))

	[print(agent) for agent in agents]