import pygame, sys, time

from pygame.locals import *
from screeninfo import get_monitors
 

pygame.init()
size=(400,300)
DISPLAYSURF = pygame.display.set_mode(size,pygame.FULLSCREEN)

pygame.display.set_caption('Panic scale')

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
sizeOfCircle = 20
increase = +2
pygame.draw.circle(DISPLAYSURF, RED, (100, 50), sizeOfCircle, 0)

while True: # main game loop
	if sizeOfCircle > 150:
		increase = -2
	elif sizeOfCircle <= 10:
		increase = 2
	sizeOfCircle = sizeOfCircle + increase
	DISPLAYSURF.fill(WHITE)
	pygame.draw.circle(DISPLAYSURF, RED, (200, 150), sizeOfCircle, 0)
	for event in pygame.event.get():
		if (event.type is KEYDOWN and event.key == K_f):
			if DISPLAYSURF.get_flags() & FULLSCREEN:
				pygame.display.set_mode((size))
			else:
				pygame.display.set_mode(size, FULLSCREEN)
		elif (event.type is KEYDOWN and event.key == K_q) or event.type == QUIT:
			pygame.quit()
			sys.exit()
	pygame.display.update()
	time.sleep(0.05)