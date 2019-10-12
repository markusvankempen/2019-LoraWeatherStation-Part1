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

print("Publish a message to LORA GW")
 
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
# connected to GPIO23.
pin = 20


_DEVICE_ID=10

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

def send_pi_data(data):
    print("Sending PI data to Lora GW")
# 
# add the temperature 
# 
    global humidity
    if humidity is None:
       humidity = 0

    msg = '{"id": %s, "t": 12, "h": %s ,"msgid": %s}' % (_DEVICE_ID,str(humidity) ,str(data))
    print(msg)
    button_a_data = bytes(msg,"utf-8")
    print(len(msg))
    rfm9x.send(button_a_data)
    #rfm9x.send(str(data))
#    lora.send_data(data_pkt, len(data_pkt), lora.frame_counter)
#    lora.frame_counter += 1
    display.fill(0)
    display.text('Sent Data '+str(data), 15, 0, 1)
    display.text('temperature ='+str(temperature), 25, 15, 1)
    display.text('humidity ='+str(humidity), 35, 25, 1)
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
