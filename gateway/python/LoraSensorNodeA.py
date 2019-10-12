from network import LoRa
import socket
import time
import pycom           # we need this module to control the LED
import ujson

pycom.heartbeat(False) # disable the blue blinking
pycom.rgbled(0x00ff00)

# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
i = 0
myping = ""
s.setblocking(False)
print("LoPy Sensor Node A v4")
while True:
    i = i + 1
    pycom.rgbled(0x000f00) # make the LED light up green in colour
    myping = ("PingLoPyA"+str(i)) #,i)
    locLoc = {'a': 0, 'o': 0}
    enc = ujson.dumps(locLoc)
    print(locLoc)
    print(locLoc)
    s.send(enc)
#    myping = ("Ping")
    print(myping)
    s.send(myping)
    print(">>> LoPy A - sending PING - "+str(i))
    time.sleep(1)
    pycom.rgbled(0x000000) # make the LED light up green in colour
    time.sleep(1)
    if s.recv(64) == b'Pong':
        print(" >>> We got a Pong back" )
    if(i>10000):
        i = 0
        pycom.rgbled(0x0000FF)
