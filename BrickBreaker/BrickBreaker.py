import pygame
import sys # use exit()
import time # use sleep()

black_screen = (0, 0, 0) # rgb format color
width = 640
height = 480

class Scene:
	def __init__(self):
		"initialization"
		self.next_scene = False
		self.playing = True

	def event_read(self, events):
		"Events logic"
		pass

	def update(self):
		"Objects logic"
		pass

	def draw(self, screen):
		"Object draw"
		pass

	def transition(self, scene):
		self.next_scene = scene

class EndGameScene(Scene):
	def update(self):
		self.playing = False

	def draw(self, screen):
		my_font = pygame.font.SysFont('Arial', 72)
		text = my_font.render('Game Over', True, (195, 160, 20))
		text_rect = text.get_rect()
		text_rect.center = [width/2, height/2]
		screen.blit(text, text_rect) 

class Level1Scene(Scene):
	def __init__(self):
		Scene.__init__(self)
		self.ball = Ball()
		self.player = Paddle()
		self.wall = Wall(80)
		self.score = 0
		self.lives = 3
		self.wait_serve = True
		# allows continous key press (miliseconds )
		pygame.key.set_repeat(15)


	def event_read(self, events):
		for event in events:
			if event.type == pygame.KEYDOWN: # looking for keyboard event, player movement
				self.player.update(event)
				if self.wait_serve and event.key == pygame.K_SPACE:
					self.wait_serve = False
					if self.ball.rect.centerx < width/2:
						self.ball.speed = [3, -3]
					else:
						self.ball.speed = [-3, -3]

	def update(self):
		# update ball's position
		if not self.wait_serve:
			self.ball.update()
		else:
			self.ball.rect.midbottom = self.player.rect.midtop

		# player-ball collision
		if pygame.sprite.collide_rect(self.ball, self.player):
			self.ball.speed[1] = -self.ball.speed[1]

		li = pygame.sprite.spritecollide(self.ball, self.wall, False) # if set to True it automatically destroys every object it touches 

		if li: # check if there are elements collided
			bk = li[0]
			cx = self.ball.rect.centerx
			if cx < bk.rect.left or cx > bk.rect.right:
				self.ball.speed[0] = -self.ball.speed[0]
			else:
				self.ball.speed[1] = -self.ball.speed[1]
			self.wall.remove(bk)
			self.score += 10

		if self.ball.rect.top > height:
			self.lives -= 1
			self.wait_serve = True

		if self.lives <= 0:
			self.next_scene = 'EndGame'

	def draw(self, screen):
		# fill screen to prevent overlaping of drawings
		screen.fill(black_screen)
		# show score
		self.update_score(screen)
		# show lives
		self.render_lives(screen)
		# blit, draws given image in given rect position
		screen.blit(self.ball.image, self.ball.rect)
		screen.blit(self.player.image, self.player.rect)
		# draw the group of sprites 
		self.wall.draw(screen)

	def update_score(self, screen):
		my_font = pygame.font.SysFont('Consola', 20)
		text = my_font.render('Score: ' + str(self.score).zfill(5), True, (255, 255, 255))
		text_rect = text.get_rect()
		text_rect.topright = [width, 0 ]
		screen.blit(text, text_rect)

	def render_lives(self, screen):
		my_font = pygame.font.SysFont('Consola', 20)
		text = my_font.render('Lives: ' + str(self.lives).zfill(2), True, (202, 44, 146))
		text_rect = text.get_rect()
		text_rect.topleft = [0, 0]
		screen.blit(text, text_rect)


class Director:
	def __init__(self, title = "", res = (width, height)):
		pygame.init() # needed for the use for custom fonts
		# clock provided by pygame
		self.clock = pygame.time.Clock()
		# create window and set its size
		self.screen = pygame.display.set_mode(res)
		# change name display on the window
		pygame.display.set_caption(title)
		self.scene =  None
		self.scenes = {}

	def run(self, start_scene, fps = 60):
		self.scene = self.scenes[start_scene]
		playing = True
		while playing:
			self.clock.tick(fps)
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT: # if click to close 
					playing = False

			self.scene.event_read(events)
			self.scene.update()
			self.scene.draw(self.screen)

			self.choose_scene(self.scene.next_scene)

			if playing:
				playing = self.scene.playing

			pygame.display.flip()
		time.sleep(1.5)

	def choose_scene(self, next_scene):
		if next_scene:
			if next_scene not in self.scenes:
				self.add_scene(next_scene)
			self.scene = self.scenes[next_scene]

	def add_scene(self, scene):
		scene_class = scene+'Scene'
		sceneObj = globals()[scene_class]
		self.scenes[scene] = sceneObj()

class Ball(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		# image load
		self.image = pygame.image.load('imagenes/ball.png')
		# get rectangle, this is used by pygame to calculate the location of the object
		self.rect = self.image.get_rect()
		# center image on screen
		self.rect.centerx = width/2
		self.rect.centery = height/2
		# alternatively self.rect.center = (width/2, height/2)
		self.speed = [3,3]

	# override 
	def update(self):
		# prevent fliying
		if self.rect.top <= 0:
			self.speed[1] = -self.speed[1]
		if self.rect.right >= width or self.rect.left <= 0:
			self.speed[0] = -self.speed[0]
		# updates the rectangle based on the movement speed defined earlier
		self.rect.move_ip(self.speed)

class Paddle(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		# image load
		self.image = pygame.image.load('imagenes/paddle.png')
		# get rectangle, this is used by pygame to calculate the location of the object
		self.rect = self.image.get_rect()
		self.rect.midbottom = (width/2, height -20)
		
		# alternatively self.rect.center = (width/2, height/2)
		self.speed = [0 , 0]

	# override 
	def update(self, event):
		if event.key == pygame.K_LEFT and self.rect.left > 0:
			self.speed = [-5, 0]
		elif event.key == pygame.K_RIGHT and self.rect.right < width:
			self.speed = [5, 0]
		else:
			self.speed = [0, 0]
		# updates the rectangle based on the movement speed defined earlier
		self.rect.move_ip(self.speed)

class Brick(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		# image load
		self.image = pygame.image.load('imagenes/brick.png')
		# get rectangle, this is used by pygame to calculate the location of the object
		self.rect = self.image.get_rect()
		# set its relative position in the group
		self.rect.topleft = pos

class Wall(pygame.sprite.Group):
	def __init__(self, cant):
		pygame.sprite.Group.__init__(self)

		pos_x = 12
		pos_y = 20
		for i in range(cant):
			brick = Brick((pos_x, pos_y))
			self.add(brick)
			if pos_x + brick.rect.width >= width - brick.rect.width:
				pos_x = 12
				pos_y += brick.rect.height
			else:
				pos_x += brick.rect.width

director = Director('BrickBreaker', (width, height))				
director.add_scene('Level1')
director.run('Level1')