#
# LoRaNanoNode.py
#

import os
import socket
import time
import struct
from network import LoRa
from uos import urandom
import pycom
from machine import Pin
from onewire import DS18X20
from onewire import OneWire


pycom.heartbeat(False) # disable the blue blinking

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
_DEVICE_ID = 0x01
_MAX_ACK_TIME = 5000
_RETRY_COUNT = 3

# Let the world know we're starting up.
pycom.rgbled(0x000101)
time.sleep(1)

print("Starting LoRaNanoNode on device %d" % _DEVICE_ID)

# Open a Lora Socket, use tx_iq to avoid listening to our own messages
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915,frequency=915000000,public=False)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

# Method to increase message id and keep in between 1 and 255
msg_id = 0
def increase_msg_id():
    global msg_id
    msg_id = (msg_id + 1) & 0xFF

# Method for acknoledge waiting time keep
def check_ack_time(from_time):
    current_time = time.ticks_ms()
    return (current_time - from_time > _MAX_ACK_TIME)
#Formats real-time clock as text
def rtc_string(time):
    return "{}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}.{:0>6d} {}".format(time[0], time[1], time[2], time[3], time[4], time[5], time[6], "GMT" if time[7] is None else time[7])

ow = OneWire(Pin('P10'))
temp = DS18X20(ow)
def get_temp(arg):
    print("Read temperature from DS18X20")
    #DS18B20 data line connected to pin P10

    temp.start_conversion()
    time.sleep(1)
    print(temp.read_temp_async())
    return(temp.read_temp_async())

# Method to send messages
def send_msg(msg):
    global msg_id
    retry = _RETRY_COUNT
    while (retry > 0 and not retry == -1):
        retry -= 1
        pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), _DEVICE_ID, len(msg), msg_id, msg)
        bytes_sent = lora_sock.send(pkg)
        print(">>>>>>>>>>>>>> Sending package %s, length = %d, bytes sent = %d" % (pkg, len(pkg), bytes_sent))

        # Wait for the response from the server.
        start_time = time.ticks_ms()

        while(not check_ack_time(start_time)):
            recv_ack = lora_sock.recv(256)
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

# Main Loop
while(True):
    mytime = time.gmtime()
    msg = '{"id": %s, "temperature": %s,"msgid": %s}' % (_DEVICE_ID ,str(get_temp(0)),str(msg_id))
    # msg = "DEVICE %d HERE" % _DEVICE_ID

    print("Sending a message: %s, length = %d" % (msg, len(msg)))

    # success = send_msg("DEVICE %d HERE" % _DEVICE_ID)
    success = send_msg(msg)
    if (success):
        print("ACK RECEIVED: %d" % msg_id)
        increase_msg_id()
    else:
        print("MESSAGE FAILED")

    time.sleep(5)
        # Manage the error message
#
# >>>>>>>>>>>>>> Sending package b'\x01I\x00{"id": 1, "temperature": -14.3,"unit": "C","time":"14-Apr-2017@21:48:32"}', length = 76
# >>>>>>>>>>>>>> Sending package b'\x01\r\x10DEVICE 1 HERE', length = 16
#
