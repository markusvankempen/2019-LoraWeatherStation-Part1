
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)

print("Soil Monitor - adjust the Pin Number≈")

GPIO.setup(21,GPIO.IN)
while True:
	if ( GPIO.input(21==GPIO.LOW) ):
		print("watery soil")
	else:
		print("Dry Soil")
