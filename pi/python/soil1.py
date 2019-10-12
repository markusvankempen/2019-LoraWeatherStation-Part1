import RPi.GPIO as GPIO
import time
 
#GPIO SETUP
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
 
def callback(channel):
        if GPIO.input(channel):
                print ("NO Water Detected!")
        else:
                print ("Water Detected!")
 
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change
 
# infinite loop
while True:
        print ("Check for Water 0=Water 1=No Water")
        print (GPIO.input(channel))
        if GPIO.input(channel):
                print ("NO Water Detected!")
        else:
                print ("Water Detected!")
        time.sleep(1)

