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
		self.angle = 0

		self.speed = 0.3 
		self.turn_speed = 0.2
		self.vision_range = 128

		# muscles
		self.muscle_forward = 1
		self.muscle_left = 0
		self.muscle_right = 0

		self.nearby = []

	def __repr__(self):
		return "Agent({}. {}, {})".format(self.index, int(self.x), int(self.y))

	def move(self):
		self.decide_movement()
		self.angle += (self.muscle_right-self.muscle_left)*self.turn_speed

		# move in direction facing
		theta_rad = radians(-self.angle)
		self.x += cos(theta_rad)*self.muscle_forward*self.speed
		self.y += sin(theta_rad)*self.muscle_forward*self.speed

		# clamp position
		self.x = max(32, min(world_w-32, self.x))
		self.y = max(32, min(world_h-32, self.y))

	def decide_movement(self):
		# split nearby into left and right
		left_items = []
		right_items = []
		for item in self.nearby:
			if item.ang < 90:
				left_items.append(item)
			else:
				right_items.append(item)

		likes = [Agent]
		dislikes = [Food]

		# score each side
		left_score =  sum([1*(1/item.dist) for item in left_items if type(item.obj) in likes]+[-1*(1/item.dist) for item in left_items if type(item.obj) in dislikes])/(len(left_items)+1)
		right_score = sum([1*(1/item.dist) for item in right_items if type(item.obj) in likes]+[-1*(1/item.dist) for item in right_items if type(item.obj) in dislikes])/(len(right_items)+1)

		# determine turn
		self.muscle_left = min(1, max(-1, left_score))
		self.muscle_right = min(1, max(-1, right_score))

	def detect_nearby(self):
		self.nearby = []
		for item in agents+foods:
			if point_distance(self.x, self.y, item.x, item.y) < self.vision_range and item != self:
				if 90 < point_direction(self.x, self.y, item.x, item.y, offset=self.angle+180) < 270:
					rel_ang = point_direction(self.x, self.y, item.x, item.y, offset=self.angle+270)
					rel_dist = 1-point_distance(self.x, self.y, item.x, item.y) / self.vision_range
					self.nearby.append(VisionItem(item, rel_ang, rel_dist))


class Food:

	def __init__(self, x, y):
		self.x = x
		self.y = y

class VisionItem:

	def __init__(self, obj, angle, distance):
		self.obj = obj
		self.ang = angle
		self.dist = distance

	def __repr__(self):
		return "VisionItem({}, {}, {})".format(self.obj, self.ang, self.dist)

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
		colors["dk_gray"] = (50, 50, 50)
		colors["black"] = (0, 0, 0)
		colors["red"] = (255, 0, 0)
		colors["yellow"] = (255, 255, 0)
		colors["lime"] = (0, 255, 0)

		fonts = {}
		fonts["small"] = pygame.font.SysFont("arial", 11)
		fonts["large"] = pygame.font.SysFont("arial", 15)

		return colors, fonts

	def main(self):
		self.display.fill((255, 255, 255))
		self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

		self.display_environment()
		self.display_agents()
		self.display_focus_info()

		pygame.display.set_caption("FPS: {}".format(round(self.clock.get_fps(),2)))

		pygame.display.update()
		self.clock.tick(60)

	def display_agents(self):
		c = self.colors
		f = self.fonts

		for agent in agents:
			x, y = int(agent.x), int(agent.y)

			# trajectory
			x2, y2 = extend_direction(x, y, agent.angle, 16)
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
			for item in self.focus.nearby:
				pygame.draw.line(self.display, c["lt_gray"], (self.focus.x, self.focus.y), (item.obj.x, item.obj.y), 1)

			# focus rect
			pygame.draw.rect(self.display, c["red"], (self.focus.x-10, self.focus.y-10, 20, 20), 2)

			# index tag
			text = f["small"].render("{}".format(self.focus.index), True, c["red"])
			text_rect = text.get_rect(center=(self.focus.x, self.focus.y-18))
			self.display.blit(text, text_rect)

	def display_environment(self):
		c = self.colors
		f = self.fonts

		for food in foods:
			x, y = int(food.x), int(food.y)
			pygame.draw.circle(self.display, c["lime"], (x, y), 3)

	def display_focus_info(self):
		c = self.colors
		f = self.fonts

		pygame.draw.rect(self.display, c["dk_gray"], (900, 0, 400, 720))

		x, y = 900, 0

		if not self.focus == None:
			fagent = self.focus

			text = f["large"].render("Agent #{}".format(fagent.index), True, c["white"])
			self.display.blit(text, (x+4, y+4))

			# agent enlarged
			x1, y1 = x+48, y+64
			pygame.draw.circle(self.display, c["gray"], (x1, y1), 24, 4)
			x2, y2 = extend_direction(x1, y1, fagent.angle, 32)
			pygame.draw.line(self.display, c["lt_gray"], (x1, y1), (x2, y2), 4)
			text = f["large"].render("{}, {}".format(int(fagent.x), int(fagent.y)), True, c["white"])
			self.display.blit(text, (x1+48, y1-20))
			text = f["large"].render("{}°".format(round(fagent.angle % 360, 1)), True, c["white"])
			self.display.blit(text, (x1+48, y1))

			# agent vision
			x, y = x, y+116
			# stats
			text = f["large"].render("{}".format(len(fagent.nearby)), True, c["white"])
			self.display.blit(text, (x+8, y+5))
			# items
			for item in fagent.nearby:
				xx = (item.ang/180)*364
				yy = (item.dist*228)
				pygame.draw.line(self.display, c["gray"], (x+8+int(xx), y+int(yy)), (x+8+int(xx), y+240), 1)
				col = {Agent: c["white"], Food: c["lime"]}[type(item.obj)]
				pygame.draw.circle(self.display, col, (x+8+int(xx), y+4+int(yy)), 4)

			pygame.draw.rect(self.display, c["lt_gray"], (x+4, y+2, 372, 240), 2)
			pygame.draw.line(self.display, c["red"], (x+8+182, y+4), (x+8+182, y+239), 1)

			# muscles
			x, y = x, y+264
			muscles = [fagent.muscle_left, fagent.muscle_forward, fagent.muscle_right]
			for i, muscle in enumerate(muscles):
				pygame.draw.circle(self.display, c["lt_gray"], (x+190-64+i*64, y+24), 20, 2)
				col = (c["red"], c["lime"])[muscle > 0]
				pygame.draw.circle(self.display, col, (x+190-64+i*64, y+24), min(18, abs(int(muscle*16))))


def initialize_world(debug=True):
	agents = []
	for i in range(64):
		new_agent = Agent(i, random.randint(32, world_w-32), random.randint(32, world_h-32))
		new_agent.angle = random.randint(0, 360)
		agents.append(new_agent)
	print("Created {} agents".format(len(agents)))

	foods = []
	for i in range(32):
		foods.append(Food(random.randint(32, world_w-32), random.randint(32, world_h-32)))
	print("Created {} foods".format(len(foods)))

	return agents, foods

def main():
	# agent loop
	for agent in agents:
		agent.detect_nearby()
		agent.move()

if __name__ == "__main__":
	world_w = 900
	world_h = 720

	running = True
	paused = False

	# init display and world
	Display = Display()
	agents, foods = initialize_world()

	while running:
		if not paused:
			# run main loop
			main()

		# run main display loop
		Display.main()

		# events
		for event in pygame.event.get():
			# keypressed
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					paused = (True, False)[paused]
			# quitting
			if event.type == pygame.QUIT:
				running = False

	pygame.quit()
	quit()