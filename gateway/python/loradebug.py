from network import LoRa
import socket
import machine
import time

lora = LoRa(mode=LoRa.LORAWAN,            region=LoRa.US915)
lora.coding_rate(LoRa.CODING_4_5)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

print("LoRa Ready")
print("Frequency: "+ str(lora.frequency()))
print("Spreading Factor: "+ str(lora.sf()))
print("Coding Rate: "+ str(lora.coding_rate()))
print("Bandwidth: "+ str(lora.bandwidth()))
print(lora.mac())


while True:
    data = s.recv(128)
    print(lora.stats())
    print(data)
    time.sleep(1)
