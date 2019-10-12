"""
Example for using the RFM9x Radio with Raspberry Pi.

Learn Guide: https://learn.adafruit.com/lora-and-lorawan-for-raspberry-pi
Author: Brent Rubell for Adafruit Industries
"""
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
m = {'id': 2, 'name': 'hussain'}
n = json.dumps(m)
o = json.loads(n)
print(o['id'], o['name'])
print(m['name'])

# A basic package header
# B: 1 byte for the deviceId
# B: 1 byte for the pkg size
# B: 1 byte for the messageId
# %ds: Formated string for string
_LORA_PKG_FORMAT = "!BBB%ds"

# A basic ack package
# B: 1 byte for the deviceId
# B: 1 byte for the pkg size
# B: 1 byte for the messageId
# B: 1 byte for the Ok (200) or error messages
_LORA_PKG_ACK_FORMAT = "BBBB"

# This device ID, use different device id for each device
_DEVICE_ID = 0x02
_MAX_ACK_TIME = 5000
_RETRY_COUNT = 3

# Method to increase message id and keep in between 1 and 255
msg_id = 0
def increase_msg_id():
    global msg_id
    msg_id = (msg_id + 1) & 0xFF

# Method for acknoledge waiting time keep
def check_ack_time(from_time):
    current_time = time.ticks_ms()
    return (current_time - from_time > _MAX_ACK_TIME)

# Method to send messages
def send_msg(msg):
    global msg_id
    retry = _RETRY_COUNT
    while (retry > 0 and not retry == -1):
        retry -= 1
        pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), _DEVICE_ID, len(msg), msg_id, msg)
        #bytes_sent = lora_sock.send(pkg)
        rfm9x.send(pkg)
        print(">>>>>>>>>>>>>> Sending package %s, length = %d, bytes sent = %d" % (pkg, len(pkg), bytes_sent))

        # Wait for the response from the server.
        start_time = time.ticks_ms()

        while(not check_ack_time(start_time)):
            #recv_ack = lora_sock.recv(256)
            recv_ack = rfm9x.receive()
            # If a message of the size of the acknoledge message is received
            if (len(recv_ack) == 4):
                device_id, pkg_len, recv_msg_id, status = struct.unpack(_LORA_PKG_ACK_FORMAT, recv_ack)
                if (device_id == _DEVICE_ID and recv_msg_id == msg_id):
                    if (status == 200):
                        # Do some code if your message arrived at the central
                        return True
                    else:
                        return False
        time.sleep_ms(urandom(1)[0] << 2)
    return False

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
def send_pi_data(data):
    # Encode float as int
#    data = int(data * 100)
    # Encode payload as bytes
#    data_pkt[0] = (data >> 8) & 0xff
#    data_pkt[1] = data & 0xff
    # Send data packet
    msg = '{"id": %s, "t": 12 ,"msgid": %s}' % (_DEVICE_ID ,str(data))
    #send_msg(msg)
#    pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), _DEVICE_ID, len(msg), str(1), msg)
#    button_a_data = bytes("PingPi"+str(data),"utf-8")
#    rfm9x.send(button_a_data)
    print(msg)

#    m = json.dumps(msg)
    button_a_data = bytes(msg,"utf-8")
    print(len(msg))
    rfm9x.send(button_a_data)
    #rfm9x.send(str(data))
#    lora.send_data(data_pkt, len(data_pkt), lora.frame_counter)
#    lora.frame_counter += 1
    display.fill(0)
    display.text('Sent Data '+str(data), 15, 15, 1)
    print('Data sent!')
    print(data)
    display.show()
    time.sleep(0.5)

while True:
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text('RasPi LoRa', 35, 0, 1)

    # check for packet rx
    packet = rfm9x.receive()
    if packet is None:
        display.show()
        display.text('- Waiting for PKT -', 15, 20, 1)
        print('Waiting ...')
    else:
        # Display the packet text and rssi
        display.fill(0)
        prev_packet = packet
        packet_text = str(prev_packet, "utf-8")
        print ('got data')
        print (packet_text)
        display.text('RX: ', 0, 0, 1)
        display.text(packet_text, 25, 0, 1)
        time.sleep(2)

    if not btnA.value:
        # Send Button A
        display.fill(0)
        button_a_data = bytes("Button A!\r\n","utf-8")
        rfm9x.send(button_a_data)
        display.text('Sent Button A!', 25, 15, 1)
    elif not btnB.value:
        # Send Button B
        display.fill(0)
        button_b_data = bytes("Button B!\r\n","utf-8")
        rfm9x.send(button_b_data)
        display.text('Sent Button B!', 25, 15, 1)
    elif not btnC.value:
        # Send Button C
        display.fill(0)
        button_c_data = bytes("PingPiC","utf-8")
        print("Button-C - Send PingPiC")
        rfm9x.send(button_c_data)
        display.text('Sent Button C!', 25, 15, 1)


    display.show()
    send_pi_data(mydata)
    mydata=mydata+1	
    time.sleep(0.1)

