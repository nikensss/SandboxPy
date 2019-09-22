#!/usr/bin/python python

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
	amountOfDistancesToAverage += 2
	distances = [0] * amountOfDistancesToAverage
	for index in range(0,amountOfDistancesToAverage):
		#index = 0
		distances[index] = getDistance()
		time.sleep(0.001)
	
	distances.remove(max(distances))
	distances.remove(min(distances))
	average = statistics.mean(distances)

	return average

def panicLevel(distance, speed):
	return (speed/(20*distance)) + 10*(speed-distance)

def smoothUpdate(newValue, oldValue):
	print("\t" + str(newValue))
	while(newValue != oldValue):
		if abs(newValue - oldValue) < 2:
			oldValue = newValue
		print("\t\t" + str(oldValue))
		halfDif = int((newValue-oldValue)/2)
		DISPLAYSURF.fill(WHITE)
		pygame.draw.circle(DISPLAYSURF, RED, center, oldValue+halfDif, 0)
		pygame.display.update()
		oldValue = oldValue + halfDif
		time.sleep(0.01) #100 us

def smoothToDefaultSize(startingValue):
	print("\t\tsmoothToDefaultSize")
	newValue = startingValue - (startingValue-50)/20
	while(newValue > 50):
		if newValue < 51:
			newValue = 50
		print("\t\t"+str(newValue))
		DISPLAYSURF.fill(WHITE)
		pygame.draw.circle(DISPLAYSURF, RED, center, int(newValue), 0)
		pygame.display.update()
		newValue = newValue - (newValue-50)/20
		time.sleep(0.01)
		


GPIO_ECHO = 17
GPIO_TRIGGER = 4
GPIO_LED = 19
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_LED,GPIO.OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

p = GPIO.PWM(GPIO_LED,100)
dc = 0.3
p.start(dc)

pygame.init()
height = 800
width = 600
midHeight = int(height/2)
midWidth = int(width/2)
maxMeasureableDistance = 400 #in cm
if midHeight >= midWidth:
	maxCircleSize = midWidth
else:
	maxCircleSize = midHeight
minCircleSize = 50
longestPanicTime = 5 #in s, indicates the time the circle will stay when max panic level is reached
center = (midHeight,midWidth)
size=(height,width)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
sizeOfCircle = 20
#measures = [0] * 100
increase = +2

DISPLAYSURF = pygame.display.set_mode(size,pygame.RESIZABLE)
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption('Panic scale')
pygame.draw.circle(DISPLAYSURF, RED, center, minCircleSize, 0)
pygame.display.update()
previousMeasure = getDistance()
previousTime = time.time()
#print("Calibrating...")
#index = 0
#for x in range(0,100):
#	measures[x] = getDistance()
#print("Calibration finished!")

while True: # main game loop
	measure = getAverageDistance(20)
	newTime = time.time()
	speed = math.fabs((measure - previousMeasure)/(newTime - previousTime))
	if speed < 1000:
		previousSizeOfCircle = sizeOfCircle
		sizeOfCircle = 3*int(panicLevel(measure,speed)/10) + minCircleSize #25 is highest value that panicLevel can return
		if sizeOfCircle > maxCircleSize:
			sizeOfCircle = maxCircleSize
		elif sizeOfCircle < minCircleSize:
			sizeOfCircle = minCircleSize
		if measure < previousMeasure:
			smoothUpdate(sizeOfCircle, previousSizeOfCircle)
			#timeToSleep = ((sizeOfCircle/maxCircleSize)**4)*longestPanicTime
			#if timeToSleep > 0:
			#	time.sleep(timeToSleep)
			smoothToDefaultSize(sizeOfCircle)

	previousTime = newTime
	previousMeasure = measure
	
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
	#time.sleep(0.01)