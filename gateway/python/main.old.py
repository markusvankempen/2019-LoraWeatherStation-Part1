from network import LoRa
import socket
import time
import pycom
pycom.heartbeat(False)

# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)
print("LoPy A v1")


while True:
    pycom.rgbled(0xf00000)  # Blue
    data =s.recv(64)
    if "Ping" in data:
        print(data)
        print(">>>>> Yeah LoPy A >> got PING message >>> sending PONG ")
        pycom.rgbled(0x00000F)  # Blue
        s.send("Pong")
    time.sleep(1)
    pycom.rgbled(0x000000)  # Blue
#    print(">>LoPy A waiting for data")
