from network import LoRa
import time
import binascii
import socket
import pycom
import struct

lora = LoRa(mode=LoRa.LORAWAN)


#corresponding real values
dev_addr = struct.unpack(">l", binascii.unhexlify('00000000'))[0]
nwk_swkey = binascii.unhexlify('00000000000000000000000000000000')
app_swkey = binascii.unhexlify('00000000000000000000000000000000')

lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

#wait until the module has joined the network
while not lora.has_joined():
    time.sleep(1.5)
    print('Not joined yet...')

print('Network joined!')

print("LoRa Ready")
print("Frequency: "+ str(lora.frequency()))
print("Spreading Factor: "+ str(lora.sf()))
print("Coding Rate: "+ str(lora.coding_rate()))
print("Bandwidth: "+ str(lora.bandwidth()))
print(lora.mac())


pycom.rgbled(0x00ff00)

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
s.setblocking(True)

while True:
    print('Sending Packet...')
    pycom.rgbled(0x00ff00)
    s.send('0')
    print('Done sending')
    data = s.recv(64)
    time.sleep(2000)
