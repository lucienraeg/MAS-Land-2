import pygame
import random
import numpy as np
import math
from math import sin, cos, radians, pi

random.seed(1)

def extend_direction(x1, y1, angle, d):
	theta_rad = radians(-angle)
	return x1 + d*cos(theta_rad), y1 + d*sin(theta_rad)

def point_distance(x1, y1, x2, y2):
	return math.sqrt(abs(x1 - x2)**2 + abs(y1 - y2)**2)

def point_direction(x1, y1, x2, y2, offset=0):
	return (180 - offset - np.rad2deg(np.arctan2(y1 - y2, x1 - x2))) % 360

class Agent:

	def __init__(self, index, x, y):
		self.index = index
		self.x, self.y = x, y
		self.turn = 0
		self.angle = 0

		self.speed = 0.5 # 0.5
		self.turn_speed = 0.1 # 0.1
		self.vision_range = 256

		self.nearby = []

	def __repr__(self):
		return "Agent({}. {}, {})".format(self.index, int(self.x), int(self.y))

	def move(self):
		self.decide_direction()

		# move in direction facing
		theta_rad = radians(-self.angle)
		self.x += self.speed*cos(theta_rad)
		self.y += self.speed*sin(theta_rad)

		# clamp position
		self.x = max(32, min(Display.width-32, self.x))
		self.y = max(32, min(Display.height-32, self.y))

	def decide_direction(self):
		# random wandering
		self.turn = max(-1, min(1, self.turn)) + random.uniform(-1, 1)*self.turn_speed
		self.angle += self.turn

	def detect_nearby(self):
		self.nearby = []
		for agent in agents:
			if point_distance(self.x, self.y, agent.x, agent.y) < self.vision_range and agent != self:
				if 90 < point_direction(self.x, self.y, agent.x, agent.y, offset=self.angle+180) < 270:
					self.nearby.append(agent)

class Display:

	def __init__(self):
		pygame.init()
		self.width, self.height = 1280, 720
		self.display = pygame.display.set_mode((self.width, self.height))
		self.clock = pygame.time.Clock()

		self.colors, self.fonts = self.init_misc()
		self.focus = None

	def init_misc(self):
		colors = {}
		colors["white"] = (255, 255, 255)
		colors["lt_gray"] = (200, 200, 200)
		colors["gray"] = (150, 150, 150)
		colors["black"] = (0, 0, 0)
		colors["red"] = (255, 0, 0)
		colors["yellow"] = (255, 255, 0)

		fonts = {}
		fonts["small"] = pygame.font.SysFont("arial", 11)
		fonts["large"] = pygame.font.SysFont("arial", 15)

		return colors, fonts

	def main(self):
		self.display.fill((255, 255, 255))
		self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

		self.display_agents()
		self.display_focus()

		pygame.display.set_caption("FPS: {}".format(round(self.clock.get_fps(),2)))

		pygame.display.update()
		self.clock.tick(60)

	def display_agents(self):
		c = self.colors
		f = self.fonts

		for agent in agents:
			x, y = int(agent.x), int(agent.y)

			# trajectory
			x2, y2 = extend_direction(x, y, agent.angle, 32)
			pygame.draw.line(self.display, c["gray"], (x, y), (x2, y2), 2)

			# body
			pygame.draw.circle(self.display, c["black"], (x, y), 5)

			# focus selection
			if pygame.mouse.get_pressed()[0]:
				if point_distance(x, y, self.mouse_x, self.mouse_y) < 16:
					self.focus = agent

		# focus box
		if not self.focus == None:

			# connections with nearby agents
			for other_agent in self.focus.nearby:
				pygame.draw.line(self.display, c["lt_gray"], (self.focus.x, self.focus.y), (other_agent.x, other_agent.y), 1)

			# focus rect
			pygame.draw.rect(self.display, c["red"], (self.focus.x-10, self.focus.y-10, 20, 20), 2)

			# index tag
			text = f["small"].render("{}".format(self.focus.index), True, c["red"])
			text_rect = text.get_rect(center=(self.focus.x, self.focus.y-18))
			self.display.blit(text, text_rect)

	def display_focus(self):
		c = self.colors
		f = self.fonts

		if not self.focus == None:
			fagent = self.focus
			text = f["large"].render("#{}, x: {}, y: {}, angle: {}°, nearby: {}".format(fagent.index, int(fagent.x), int(fagent.y), int(fagent.angle % 360), [agent.index for agent in fagent.nearby]), True, c["black"])
			self.display.blit(text, (4, 4))

			pygame.draw.rect(self.display, c["black"], (4, 24, 182, 16), 2)
			pygame.draw.rect(self.display, c["red"], (4+90, 24, 1, 16), 2)

			if len(fagent.nearby):
				for i, agent in enumerate(fagent.nearby):
					rel_ang = point_direction(fagent.x, fagent.y, agent.x, agent.y, offset=fagent.angle+270)
					rel_dist = 1-point_distance(fagent.x, fagent.y, agent.x, agent.y) / agent.vision_range

					col = (int(255*(0.5+rel_dist/2)), 0, 0)

					pygame.draw.circle(self.display, col, (int(4+(rel_ang)), 32), 3)


def initialize_world(debug=True):
	agents = []
	for i in range(64):
		agents.append(Agent(i, random.randint(32, Display.width-32), random.randint(32, Display.height-32)))

	print("Created {} agents".format(len(agents)))

	return agents

def main():
	# agent loop
	for agent in agents: 
		agent.detect_nearby()
		agent.move()

if __name__ == "__main__":
	running = True

	# init display and world
	Display = Display()
	agents = initialize_world()

	while running:
		# run main loop
		main()

		# run main display loop
		Display.main()

		# events
		for event in pygame.event.get():
			# quitting
			if event.type == pygame.QUIT:
				running = False

	pygame.quit()
	quit()