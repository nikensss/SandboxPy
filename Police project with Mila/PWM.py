import RPi.GPIO as GPIO
import time

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
increase = 5
p.start(dc)

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

try:
	while True:
		distanceMeasured = getDistance()
		dc = (1-(distanceMeasured/500))*100 #the closer, the brighter the led
		if dc > 100:
			dc = 100
		elif dc < 0:
			dc = 0
		p.ChangeDutyCycle(dc)
		time.sleep(1)
		print("The measured distance was: " + str(round(distanceMeasured, 2)) + " cm (dc = " + str(dc) + "%)")
except KeyboardInterrupt:
	p.stop()
	GPIO.cleanup()