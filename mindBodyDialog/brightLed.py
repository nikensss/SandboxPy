import RPi.GPIO as GPIO
import time
from numpy import interp, average

GPIO_ECHO = 17
GPIO_TRIGGER = 4
GPIO_LED = 14
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_LED,GPIO.OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

p = GPIO.PWM(GPIO_LED,100)
dc = 0
increase = 5
p.start(dc)

#The distance sensor can sense up to 300cm
#We have to map from 20 to 300 between 0% and 100%
def map(distance):
    return interp(distance, [15,300],[0,100])

def getDistance():
    # set Trigger to LOW
    GPIO.output(GPIO_TRIGGER, GPIO.LOW)
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, GPIO.HIGH)
    
    # set Trigger after 10 us to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, GPIO.LOW)
    
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
    distance = round((TimeElapsed * 34300) / 2,2)
    #print('distance: ' + str(distance) + ' cm')
    return distance

def getAverageDistance():
    distances = []
    for i in range(0,20):
        distances.append(getDistance())
    
    #print(str(distances))
    return round(average(distances),2)
try:
    while True:
        distanceMeasured = getAverageDistance()
        dc = map(distanceMeasured) #the further, the brighter the led
        p.ChangeDutyCycle(dc)
        time.sleep(0.15)
        print(str(distanceMeasured) + " cm (dc = " + str(round(dc,2)) + "%)")
finally:
    print('Finally')
    p.ChangeDutyCycle(0)
    p.stop()
    GPIO.cleanup()