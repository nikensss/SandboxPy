import pygame, sys, time, math, statistics
import RPi.GPIO as GPIO
from pygame.locals import *

def getDistance():
	# set Trigger to LOW
	GPIO.output(GPIO_TRIGGER, False)
	# set Trigger to HIGH
	GPIO.output(GPIO_TRIGGER, True)
	
	# set Trigger after 10 us to LOW
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIGGER, False)
	
	StartTime = time.time()
	StopTime = time.time()
	
	# save StartTime
	while GPIO.input(GPIO_ECHO) == 0:
		StartTime = time.time()
	
	# save time of arrival
	while GPIO.input(GPIO_ECHO) == 1:
		StopTime = time.time()
	
	# time difference between start and arrival
	TimeElapsed = StopTime - StartTime
	# multiply with the sonic speed (34300 cm/s)
	# and divide by 2, because there and back
	distance = (TimeElapsed * 34300) / 2
	
	return distance

def getAverageDistance(amountOfDistancesToAverage):
	distances = [0] * amountOfDistancesToAverage
	for index in range(0,amountOfDistancesToAverage):
		distances[index] = getDistance()
		time.sleep(0.001)
	
	average = statistics.mean(distances)

	return average

def panicLevel(distance, speed):
	return (speed/(20*distance)) + 10*(speed-distance)

GPIO_ECHO = 17
GPIO_TRIGGER = 4
GPIO_LED = 19
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_LED,GPIO.OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

p = GPIO.PWM(GPIO_LED,100)
dc = 0
p.start(dc)

pygame.init()
height = 800
width = 600
midHeight = int(height/2)
midWidth = int(width/2)
maxMeasureableDistance = 150
if midHeight >= midWidth:
	maxCircleSize = midWidth
else:
	maxCircleSize = midHeight
minCircleSize = 20
center = (midHeight,midWidth)
size=(height,width)
DISPLAYSURF = pygame.display.set_mode(size,pygame.RESIZABLE)

pygame.display.set_caption('Panic scale')

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
sizeOfCircle = 20
#measures = [0] * 100
increase = +2
pygame.draw.circle(DISPLAYSURF, RED, (100, 50), sizeOfCircle, 0)
previousMeasure = getDistance()
previousTime = time.time()
#print("Calibrating...")
#index = 0
#for x in range(0,100):
#	measures[x] = getDistance()
#print("Calibration finished!")

while True: # main game loop
	measure = getAverageDistance(10)
	newTime = time.time()
	speed = math.fabs((measure - previousMeasure)/(newTime - previousTime))
	if speed < 1000:
		sizeOfCircle = int(panicLevel(measure,speed)/10) + minCircleSize #25 is highest value that panicLevel can return
		dc = (1-(measure/maxMeasureableDistance))*100 #the closer, the brighter the led
		if dc > 80:
			dc = 80
		elif dc < 0:
			dc = 0
		if sizeOfCircle > maxCircleSize:
			sizeOfCircle = maxCircleSize
		elif sizeOfCircle < minCircleSize:
			sizeOfCircle = minCircleSize
		DISPLAYSURF.fill(WHITE)
		previousTime = newTime
		previousMeasure = measure
		pygame.draw.circle(DISPLAYSURF, RED, center, sizeOfCircle, 0)
		pygame.display.update()
		p.ChangeDutyCycle(dc)
		print("Distance: " + str(round(measure,2)) + " cm; Speed: "+ str(round(speed,2)) + " cm/s")
	
	for event in pygame.event.get():
		if (event.type is KEYDOWN and event.key == K_f):
			if DISPLAYSURF.get_flags() & FULLSCREEN:
				pygame.display.set_mode((size))
			else:
				pygame.display.set_mode(size, FULLSCREEN)
		elif (event.type is KEYDOWN and event.key == K_q) or event.type == QUIT:
			pygame.quit()
			sys.exit()
	time.sleep(0.01)