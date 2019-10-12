from network import LoRa
import socket
import time

lora = LoRa(mode=LoRa.LORAWAN, public=True, adr=False)

#Setting up channels for sub-band 2 for TTN
for index in range(0, 8):
    lora.remove_channel(index)

for index in range(16, 65):
    lora.remove_channel(index)

for index in range(66, 72):
    lora.remove_channel(index)

auth = (bytes([... ]),
        bytes([... ]))

print("joining...")
lora.join(activation=LoRa.OTAA, auth=auth, timeout=0)

x=0
# wait until the module has joined the network
while (not lora.has_joined() and x<10):
    time.sleep(2.5)
    print('Not yet joined...')
    x=x+1
    print(lora.has_joined())


if (lora.has_joined()):
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    lora.remove_channel(65); #drop the 500khz channel
    for index in range(0, 20):
        s.send("test1234567");
