
#
# This program send temperature and humidity data via lora to a GW 
# mvk@ca.ibm.com
#
#pull_up_down=GPIO.PUD_DOWN)

import Adafruit_DHT
import time
# Import Python System Libraries
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x
import struct
import json
import datetime
print("Publish a message to LORA GW")
import time

# DS20B waterproof temp 
from w1thermsensor import W1ThermSensor
dssensor = W1ThermSensor()
dssensor.gpio=4 #Not sure where to change that yet ????
#https://github.com/timofurrer/w1thermsensor
#while True:
#    temperature = sensor.get_temperature()
#    print("The temperature is %s celsius" % temperature)
#    time.sleep(1)
import RPi.GPIO as GPIO

# SOIL / Water sensor
#GPIO SETUP
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#def callback(channel):
#        if GPIO.input(channel):

 
# Wait for 5 seconds#
#time.sleep(5)

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
rfm9x.tx_power = 20
prev_packet = None
data_pkt = bytearray(512)
# time to delay periodic packet sends (in seconds)
data_pkt_delay = 3.0
mydata = 0

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP
print("Lora init") 
# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT11


# Example using a Raspberry Pi with DHT sensor
# connected to GPIO2.
pin = 13 


_DEVICE_ID=10

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

def send_pi_data(data):
    print("Sending PI data to Lora GW")
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
# 
# add the temperature 
# 
#    global humidity
    if humidity is None:
       humidity = 0

    if temperature is None:
       temperature = 0
#waterproof sensor

    ot = dssensor.get_temperature()
    if ot is None:
       ot = 0

    water=GPIO.input(channel)
    if water is None:
       water = 1
#
    if water == 0:
       watertxt = "Yes"
    else:
       watertxt = "No"
		

    #now = datetime.now()
    #now = datetime.datetime.now()
    ts = int(round(time.time() * 1000))

    msg = '{"id": %s, "h": %s, "t": %s, "ot":%s, "w":%s, "ts":%s ,"msgid": %s}' % (_DEVICE_ID,str(humidity),str(temperature),str(ot),str(water),str(ts),str(data))
    print(msg)
    button_a_data = bytes(msg,"utf-8")
    print(len(msg))
    rfm9x.send(button_a_data)
    #rfm9x.send(str(data))
#    lora.send_data(data_pkt, len(data_pkt), lora.frame_counter)
#    lora.frame_counter += 1
    display.fill(0)
    display.text('Sent'+str(data), 15, 0, 1)
    display.text('t= '+str(temperature), 15, 10, 1)
    display.text('h='+str(humidity), 75, 10, 1)
    display.text('ot='+str(ot), 15, 20, 1)
    display.text('water='+str(watertxt), 75, 20, 2)

    print('Data sent no '+str(data))
#    print(data)
    display.show()
    time.sleep(0.5)


print("lets go")
while True:
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text('RasPi LoRa', 35, 0, 1)
    now = datetime.datetime.now()
   #print ("Current date and time : ")
#print (now.strftime("%Y-%m-%d %H:%M:%S"))
    display.text(now.strftime("%Y-%m-%d %H:%M:%S"), 10, 15, 1)

    if not btnA.value:
        # Send Button A
        display.fill(0)
        display.text('temperature ='+str(temperature), 25, 15, 1)
        time.sleep(5)

    display.show()
    send_pi_data(mydata)
    mydata=mydata+1
    time.sleep(3)



# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!
#while 1:
#	if humidity is not None and temperature is not None:
#    		print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)	)
#	else:
#    		print('Failed to get reading. Try again!')
#	time.sleep(2)
