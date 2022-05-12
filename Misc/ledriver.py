import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.cleanup()
BuzzerPin = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(BuzzerPin,GPIO.OUT)
###Amarillo
GPIO.output(16,GPIO.HIGH)
time.sleep(0.5)
GPIO.output(16,GPIO.LOW)
#Rojo
GPIO.output(20,GPIO.HIGH)
time.sleep(0.5)
GPIO.output(20,GPIO.LOW)
##Verde
GPIO.output(21,GPIO.HIGH)
time.sleep(0.5)
GPIO.output(21,GPIO.LOW)
#BEEP
GPIO.output(BuzzerPin,GPIO.HIGH)
time.sleep(0.5)
GPIO.output(BuzzerPin,GPIO.LOW)
##Asumimos que estamos conectados
#GPIO.output(16,GPIO.HIGH)

##Asumimos puerta cerrada
GPIO.output(20,GPIO.HIGH)
def Buzz():
        GPIO.output(BuzzerPin,GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(BuzzerPin,GPIO.LOW)
def opendoor ():
	GPIO.output(20,GPIO.LOW)
	GPIO.output(21,GPIO.HIGH)
	Buzz()
	print("Oppened")
	time.sleep(0.5)
	GPIO.output(21,GPIO.LOW)
	GPIO.output(20,GPIO.HIGH)


def YellowBlink():
	GPIO.output(16,GPIO.HIGH)
	time.sleep(0.5)
	GPIO.output(16,GPIO.LOW)



