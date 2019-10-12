# Import Python System Libraries
import time
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

print("Button Test")

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

while True:
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text('Button Test', 35, 0, 1)

    
    if not btnA.value:
        # Send Button A
        display.fill(0)
        #button_a_data = bytes("Button A!\r\n","utf-8")
        #rfm9x.send(button_a_data)
        display.text('Sent Button A!', 25, 15, 1)
        time.sleep(1)

    display.show()
    time.sleep(0.1)

	
