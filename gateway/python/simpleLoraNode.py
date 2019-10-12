import os
import socket
import time
import struct
from network import LoRa
import pycom
from machine import Pin
from onewire import DS18X20
from onewire import OneWire
import json
pycom.heartbeat(False)
print("DS18X20")
#DS18B20 data line connected to pin P10
ow = OneWire(Pin('P10'))
temp = DS18X20(ow)



# A basic package header, B: 1 byte for the deviceId, B: 1 byte for the pkg size
_LORA_PKG_FORMAT = "BB%ds"
_LORA_PKG_ACK_FORMAT = "BBB"
DEVICE_ID = 0x01


pycom.heartbeat(False) # disable the blue blinking
# Open a Lora Socket, use tx_iq to avoid listening to our own messages
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORA, tx_iq=True, region=LoRa.US915)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)
print("Simple Lora raw Node")
pycom.rgbled(0x000022)
while(True):
    temp.start_conversion()
    time.sleep(1)
    print(temp.read_temp_async())
    # Package send containing a simple string
    msg = "Device 1 Here"
    n = {'t': temp.read_temp_async(), 'id': 'd01'}
    msg = json.dumps(n)
    pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), DEVICE_ID, len(msg), msg)
    lora_sock.send(pkg)
    print(pkg)
    # Wait for the response from the gateway. NOTE: For this demo the device does an infinite loop for while waiting the response. Introduce a max_time_waiting for you application
    waiting_ack = True
    while(waiting_ack):
        recv_ack = lora_sock.recv(256)

        if (len(recv_ack) > 0):
            device_id, pkg_len, ack = struct.unpack(_LORA_PKG_ACK_FORMAT, recv_ack)
            if (device_id == DEVICE_ID):
                if (ack == 200):
                    waiting_ack = False
                    # If the uart = machine.UART(0, 115200) and os.dupterm(uart) are set in the boot.py this print should appear in the serial port
                    print("GW ACK received")
                    pycom.rgbled(0x000200)
                else:
                    waiting_ack = False
                    # If the uart = machine.UART(0, 115200) and os.dupterm(uart) are set in the boot.py this print should appear in the serial port
                    print("Message Failed")
    print("Waiting for ACK")
    time.sleep(2)
    pycom.rgbled(0x000000)
    time.sleep(3)
