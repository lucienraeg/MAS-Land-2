import numpy as np
import pygame

def nonlin(x, deriv=False):
	if deriv:
		return x*(1-x) # sigmoid deriv
	return 1/(1+np.exp(-x)) # sigmoid

class NeuralNetwork():

	def __init__(self, l0_size, l1_size, l2_size):

		# init synapses
		np.random.seed(1)
		self.network_shape = (l0_size, l1_size, l2_size)
		self.syn0 = 2*np.random.random((self.network_shape[0], self.network_shape[1])) - 1
		self.syn1 = 2*np.random.random((self.network_shape[1], self.network_shape[2])) - 1

	def train(self, X, y, epochs=60001, visualization_step_size=10000):
		for i in range(0, epochs):

			# forward propogation
			l0 = X
			l1 = nonlin(np.dot(l0, self.syn0))
			l2 = nonlin(np.dot(l1, self.syn1))

			# error
			l2_error = y - l2

			if i % visualization_step_size == 0:
				E = np.mean(np.abs(l2_error))
				print("E: {}".format(E))
				Visualizer.update_info_bar("Epoch {}, E: {}".format(i, round(E, 6)))

				for set_n in range(len(X)):
					Visualizer.update_neural_network_visualization(self.network_shape, l0[set_n], l1[set_n], l2[set_n], self.syn0, self.syn1)

			# dir of target l2
			l2_delta = l2_error*nonlin(l2, deriv=True)

			# hidden layer error
			l1_error = l2_delta.dot(self.syn1.T)

			# dir of target l1
			l1_delta = l1_error * nonlin(l1, deriv=True)

			# update weights
			self.syn0 += l0.T.dot(l1_delta)
			self.syn1 += l1.T.dot(l2_delta)

	def predict(self, X):
		l0 = X
		l1 = nonlin(np.dot(l0, self.syn0))
		l2 = nonlin(np.dot(l1, self.syn1))

		Visualizer.update_neural_network_visualization(self.network_shape, l0, l1, l2, self.syn0, self.syn1)

		return(l2)


class Visualizer():

	def __init__(self):

		pygame.init()

		# CONSTANTS
		self.colors = {"WHITE": (255, 255, 255), "LT_GRAY": (77, 166, 111), "GRAY": (10, 56, 68), "DK_GRAY": (0, 43, 54)}
		self.FNT_TINY = pygame.font.SysFont("courier new", 12, bold=True)
		self.FNT_SMALL = pygame.font.SysFont("courier new", 20, bold=True)

		self.display_width, self.display_height = 1280, 720

		self.display = pygame.display.set_mode((self.display_width, self.display_height))
		# self.clock = pygame.time.Clock()
		self.display.fill(self.colors["DK_GRAY"])

		pygame.display.update()

	def draw_neuron(self, x, y, val):
		col = (255*val, 255*val, 255*val)
		col_neg = (255*(1-val), 255*(1-val), 255*(1-val))

		# helper function to draw neurons
		pygame.draw.circle(self.display, col, (x, y), 23)
		pygame.draw.circle(self.display, self.colors["WHITE"], (x, y), 24, 2)

		text = self.FNT_TINY.render(str(float(round(val, 3))), True, col_neg)
		text_rect = text.get_rect(center=(x,y))
		self.display.blit(text, text_rect)

	def draw_synapse(self, x1, y1, x2, y2, col):
		# helper function to draw synapses
		pygame.draw.line(self.display, col, (x1, y1), (x2, y2), 2)

	def update_info_bar(self, info_text):
		pygame.draw.rect(self.display, self.colors["GRAY"], (0, 0, self.display_width, 28))

		text = self.FNT_SMALL.render(info_text, True, self.colors["LT_GRAY"])
		self.display.blit(text, (4, 4))

		pygame.display.update()

	def update_neural_network_visualization(self, network_shape, l0, l1, l2, syn0, syn1):
		x1, y1 = 64, 96

		layer_vals = (l0, l1, l2)

		layer_gap = 150

		# draw synapses
		for syn_group_n, syn_group in enumerate([syn0, syn1]):
			for syn_set_n, syn_set in enumerate(syn_group):
				for syn_n, syn in enumerate(syn_set):
					syn_x1 = x1+(syn_group_n*layer_gap)
					syn_y1 = y1+(syn_set_n*64)
					syn_x2 = x1+((syn_group_n+1)*layer_gap)
					syn_y2 = y1+(syn_n*64)

					val = nonlin(syn)
					col = (255*val, 255*val, 255*val)

					self.draw_synapse(syn_x1, syn_y1, syn_x2, syn_y2, col)

		# draw neurons
		for layer_n, layer_size in enumerate(network_shape):
			for neuron_n in range(layer_size):
				# give txt label
				val = layer_vals[layer_n][neuron_n]

				self.draw_neuron(x1+(layer_n*layer_gap), y1+(neuron_n*64), val)

		pygame.display.update()

if __name__ == "__main__":
	running = True

	Visualizer = Visualizer()

	X = np.array([
		[0, 0, 1],
		[0, 1, 1],
		[1, 0, 1],
		[1, 1, 1]])

	y = np.array([
		[0],
		[1],
		[1],
		[0]])

	clf = NeuralNetwork(len(X[0]), 4, 1)

	clf.train(X, y)
	
	# pred_y = clf.predict([0, 1, 1])

	# print(pred_y)

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

	pygame.quit()