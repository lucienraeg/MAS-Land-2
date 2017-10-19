import pygame
import random
import agent

random.seed(1)

class Agent:

	def __init__(self, index, coords, attrs):
		self.coords = coords
		self.attrs = attrs

		self.birth = step
		self.energy = 1

		self.index = index

		self.brain = agent.Brain()

	def __repr__(self):
		return "Agent({}, {})".format(self.index, self.coords, self.attrs)

	def move(self):
		for a in [a for a in agents if a.coords == self.coords]:
			if a.index != self.index:
				self.brain.experiences.append(a)

		# random move 1 cell (8 dirs)
		new_x = max(0, min(World.world_width-1, self.coords[0] + random.randint(-1, 1)))
		new_y = max(0, min(World.world_height-1, self.coords[1] + random.randint(-1, 1)))

		self.coords = (new_x, new_y)

class World:

	def __init__(self):
		pygame.init()

		# init world
		self.cell_size = 16 # px size of cell
		self.world_width = 90
		self.world_height = 50

		# init display
		self.display_width = self.world_width*self.cell_size
		self.display_height = self.world_height*self.cell_size
		self.display = pygame.display.set_mode((self.display_width, self.display_height))

		# init font
		self.FNT_TINY = pygame.font.SysFont("arial", 9)
		self.FNT_SMALL = pygame.font.SysFont("arial", 11)
		self.FNT_MEDIUM = pygame.font.SysFont("arial", 14)
		self.FNT_LARGE = pygame.font.SysFont("arial", 24)

		# init pygame misc
		self.clock = pygame.time.Clock()
		self.button_cooldown = 0

		# init focus
		self.focus = None

	def main(self):
		self.display.fill(Color.WHITE)

		mouse_x, mouse_y = pygame.mouse.get_pos()

		# display loop
		if True:
			self.display_agents(agents)
			self.display_cursor(mouse_x, mouse_y, agents)
			self.display_hud()

		pygame.display.set_caption("FPS: {}".format(round(self.clock.get_fps(),2)))

		self.button_cooldown -= 1/60

		pygame.display.update()
		self.clock.tick(60)

	def step_string(self, step):
		return (str(step), str((step//100)/10) + "k")[step >= 1000]

	def display_toggle_button(self, x, y, text):
		mouse_x, mouse_y = pygame.mouse.get_pos()
		size = 24
		col = Color.LT_GRAY

		if x < mouse_x < x+24 and y < mouse_y < y+24:
			col = Color.GRAY
			# if pygame.mouse.get_pressed()[0] and self.button_cooldown <= 0:
			# 	self.button_cooldown = 0.5

		pygame.draw.rect(self.display, col, (x, y, size, size))

		text = self.FNT_SMALL.render("{}".format(text), True, Color.BLACK)
		text_rect = text.get_rect(center=(x+size/2, y+size/2))
		self.display.blit(text, text_rect)

		return x < mouse_x < x+24 and y < mouse_y < y+24 and pygame.mouse.get_pressed()[0] and self.button_cooldown <= 0

	def display_hud(self):
		pygame.draw.rect(self.display, Color.WHITE, (4, 4, 160, 48))
		pygame.draw.rect(self.display, Color.LT_GRAY, (4, 4, 160, 48), 2)
		text = self.FNT_LARGE.render("{}".format(self.step_string(step)), True, Color.BLACK)
		self.display.blit(text, (10, 6))
		text = self.FNT_MEDIUM.render("Pop: {}".format(self.step_string(len(agents))), True, Color.BLACK)
		self.display.blit(text, (10, 33))

		# buttons
		global paused
		if self.display_toggle_button(126, 16, ("R", "II")[paused]): 
			paused = (1, 0)[paused]
			self.button_cooldown = 0.5

		# focus panels
		if self.focus != None:
			self.display_agent_summary(self.focus, 4, 56)
			self.display_agent_brain(self.focus, 4, 184)

	def display_agent_summary(self, agent_i, x, y):
		a = agents[agent_i]

		col = (a.attrs[0]*255, a.attrs[1]*255, a.attrs[2]*255)

		# box and line
		box_w, box_h = 160, 124
		box_x, box_y = x, y
		pygame.draw.line(self.display, col, (x+box_w//2, y+box_h//2), (a.coords[0]*self.cell_size+(self.cell_size/2), a.coords[1]*self.cell_size+(self.cell_size/2)), 1)
		pygame.draw.rect(self.display, Color.WHITE, (box_x, box_y, box_w, box_h))
		pygame.draw.rect(self.display, col, (box_x, box_y, box_w, box_h), 2)

		# index
		text = self.FNT_LARGE.render("#{}".format(agent_i), True, Color.LT_GRAY)
		self.display.blit(text, (box_x+6, box_y+3))

		# energy bar
		pygame.draw.rect(self.display, Color.LT_GRAY, (box_x+box_w-50-6, box_y+6, 50, 16))
		pygame.draw.rect(self.display, Color.LIME, (box_x+box_w-50-6, box_y+6, a.energy*50, 16))
		pygame.draw.rect(self.display, Color.GRAY, (box_x+box_w-50-6, box_y+6, 50, 15), 2)
		text = self.FNT_SMALL.render("{}%".format(int(a.energy*100)), True, Color.BLACK)
		text_rect = text.get_rect(center=(box_x+box_w-25-6, box_y+6+8))
		self.display.blit(text, text_rect)

		# info
		info = ["age: " + self.step_string(step - a.birth), "coords: " + str(a.coords), "attrs: " + str(a.attrs)]

		for i, e in enumerate(info):
			text = self.FNT_MEDIUM.render("{}".format(e), True, Color.GRAY)
			self.display.blit(text, (box_x+6, box_y+30+(i*15)))

		# attr bars
		attr_cols = ((255, 0, 0), (0, 255, 0), (0, 0, 255))
		for i, attr in enumerate(a.attrs):
			pygame.draw.rect(self.display, Color.LT_GRAY, (box_x+6, box_y+80+(i*14), 110, 10))
			pygame.draw.rect(self.display, attr_cols[i], (box_x+6, box_y+80+(i*14), a.attrs[i]*110, 10))
			text = self.FNT_TINY.render("{}".format(attr), True, Color.GRAY)
			self.display.blit(text, (box_x+116+4, box_y+80+(i*14)))

	def display_agent_brain(self, agent_i, x, y):
		a = agents[agent_i]
		b = a.brain

		# box
		box_w, box_h = 160, 124
		box_x, box_y = x, y
		pygame.draw.rect(self.display, Color.WHITE, (box_x, box_y, box_w, box_h))
		pygame.draw.rect(self.display, Color.LT_GRAY, (box_x, box_y, box_w, box_h), 2)

		# experiences
		text = self.FNT_MEDIUM.render("experiences: {}".format(len(b.experiences)), True, Color.GRAY)
		self.display.blit(text, (box_x+6, box_y+6))

	def display_cursor(self, mouse_x, mouse_y, agents):
		# cell mouse coords
		cmouse_x = mouse_x // self.cell_size
		cmouse_y = mouse_y // self.cell_size

		# grid-locked mouse coords
		gmouse_x = cmouse_x * self.cell_size
		gmouse_y = cmouse_y * self.cell_size

		for a in [a for a in agents if a.coords == (cmouse_x, cmouse_y)]:
			self.display_agent_summary(a.index, mouse_x+12, mouse_y+12)

			if pygame.mouse.get_pressed()[0]:
				self.focus = a.index

	def display_agents(self, agents):
		for a in agents:
			coords = a.coords
			col = Color.attr_to_rgb(a.attrs)
			pygame.draw.rect(self.display, col, (coords[0]*self.cell_size+1, coords[1]*self.cell_size+1, 14, 14))

class Color:

	def __init__(self):
		self.BLACK = (0, 0, 0)
		self.GRAY = (120, 120, 120)
		self.LT_GRAY = (220, 220, 220)
		self.WHITE = (255, 255, 255)
		self.RED = (255, 0, 0)
		self.LIME = (0, 255, 0)

	def attr_to_rgb(self, attrs):
		return (attrs[0]*255, attrs[1]*255, attrs[2]*255)


if __name__ == "__main__":
	real_step = 0
	step = 0
	step_time = 10

	# init misc
	Color = Color()

	# init agents
	agents = []
	for i in range(0, 100):
		coords = (random.randint(0, 90), random.randint(0, 50))
		attrs = (random.randint(0, 100)/100, random.randint(0, 100)/100, random.randint(0, 100)/100)
		agents.append(Agent(i, coords, attrs))

	# init world
	World = World()

	running = True
	paused = False
	while running:

		# main loop
		real_step += 1
		World.main()

		if not paused:
			for i, a in enumerate(agents):
				if (real_step+i) % step_time == 0:
					if i == 0:
						step += 1
					a.move()

		# events
		for event in pygame.event.get():
			if event.type == pygame.QUIT: # quitting
				running = False

	pygame.quit()
	quit()