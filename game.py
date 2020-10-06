import pygame
import neat
import os
import random

# Settings
TITLE = "Flappy Bird"
WIDTH = 350
HEIGHT = 550
FPS = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Assets
game_folder = os.path.dirname(__file__)
image_folder = os.path.join(game_folder, "images")

bird_one_image = pygame.image.load(os.path.join(image_folder, "bird1.png")).convert()
bird_two_image = pygame.image.load(os.path.join(image_folder, "bird2.png")).convert()
bird_three_image = pygame.image.load(os.path.join(image_folder, "bird3.png")).convert()

pipe_image = pygame.image.load(os.path.join(image_folder, "pipe.png")).convert()
base_image = pygame.image.load(os.path.join(image_folder, "base.png")).convert()
background_image = pygame.image.load(os.path.join(image_folder, "background-day.png")).convert()

# Load images
BIRD_IMAGES = [bird_one_image, bird_one_image,
				bird_two_image, bird_two_image,
				bird_three_image, bird_three_image]

PIPE_IMAGE = pipe_image
BASE_IMAGE = base_image
BACKGROUND_IMAGE = background_image
STAT_FONT = pygame.font.SysFont("comicsans", 24)

draw_lines = True
generation = 0

class Bird:
	IMAGES = BIRD_IMAGES
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.index = 0
		self.image = self.IMAGES[self.index]
		self.bird_movement = 0
		self.gravity = 1

	def move(self):
		self.index += 1
		if self.index >= len(self.IMAGES):
			self.index = 0
		self.image = self.IMAGES[self.index]
		self.image = pygame.transform.rotozoom(self.image, -self.bird_movement*2, 1)
		
		if self.bird_movement > 18:
			self.image = self.IMAGES[0]
			self.image = pygame.transform.rotozoom(self.image, -75, 1)

		self.image.set_colorkey(BLACK)
		self.bird_movement += self.gravity
		self.y += self.bird_movement

	def jump(self):
		self.bird_movement = -10.5

	def draw(self, win):
		win.blit(self.image, (self.x, self.y))

	def get_mask(self):
		return pygame.mask.from_surface(self.image)

class Pipe:
	GAP = 100
	VEL = 4
	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
		self.PIPE_BOTTOM = PIPE_IMAGE

		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 250)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x- bird.x, self.top - round(bird.y))
		bottom_offset = (self.x- bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point:
			return True

		return False

class Base:
	VEL = 4
	def __init__(self, y):
		self.image = pygame.transform.scale(BASE_IMAGE, (WIDTH*2, 100))
		self.x = 0
		self.y = y
		self.vel = self.VEL


	def move(self):
		self.x += -self.vel
		if self.x < -WIDTH:
			self.x = 0

	def draw(self, win):
		win.blit(self.image, (self.x, self.y))


def draw_everything(bg, base, birds, pipes, score, generation, pipe_ind):
	screen.blit(bg, (0, 0))
	for pipe in pipes:
		pipe.draw(screen)

	for bird in birds:
		if draw_lines:
			try:
				pygame.draw.line(screen, RED, (bird.x+bird.image.get_width()/2, bird.y + bird.image.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 3)
				pygame.draw.line(screen, RED, (bird.x+bird.image.get_width()/2, bird.y + bird.image.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 3)
			except:
				pass
		bird.draw(screen)

	base.draw(screen)

	score_text = STAT_FONT.render("Score: " + str(score), 1, WHITE)
	screen.blit(score_text, (WIDTH-score_text.get_width()-10, 10))

	generation_count_text = STAT_FONT.render("Gen: " + str(generation), 1, WHITE)
	screen.blit(generation_count_text, (10, 10))

	alive_count_text = STAT_FONT.render("Alive: " + str(len(birds)), 1, WHITE)
	screen.blit(alive_count_text, (10, 35))

def main(genomes, config):
	global generation
	generation += 1
	bg = pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT))
	base = Base(HEIGHT-100)

	nets = []
	ge = []
	birds = []
	
	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(100, 200))
		g.fitness = 0
		ge.append(g)


	pipes = [Pipe(WIDTH)]
	score = 0
	running = True

	while running:

		clock.tick(FPS)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				pygame.quit()
				quit()

		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1
		else:
			running = False
			break

		for x, bird in enumerate(birds):
			bird.move()
			ge[x].fitness += 0.1

			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
			if output[0] > 0.5:
				bird.jump()
		
		add_pipe = False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birds):

				if pipe.collide(bird):
					ge[x].fitness -= 1
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
					rem.append(pipe)

			pipe.move()


		if add_pipe:
			score += 1
			pipes.append(Pipe(WIDTH))
			for g in ge:
				g.fitness += 5

		for r in rem:
			pipes.remove(r)


		# If bird hits the floor
		for x, bird in enumerate(birds):
			if bird.y + bird.image.get_height() >= HEIGHT-100 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

		base.move()
		draw_everything(bg, base, birds, pipes, score, generation, pipe_ind)

		pygame.display.update()

def run(config_file):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
							neat.DefaultSpeciesSet, neat.DefaultStagnation,
							config_file)
	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main, 50)

if __name__ == "__main__":
	config_file = os.path.join(game_folder, 'config-feedforward.txt')
	run(config_file)
