from network import LoRa
import socket
import machine
import time

# initialise LoRa in LORA mode
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915, frequency=915000000, tx_power=14,sf=12)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

while True:
    # send some data
    s.setblocking(False)
    s.send('Hello world !!')

    print("I sent hello !")
    print(lora.stats())
    # wait a random amount of time
    time.sleep(1)
