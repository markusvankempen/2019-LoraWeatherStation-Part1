
#
# LoRaNanoGateway.py
#
# mvk@ca.ibm.com - 2019-oct-10
#
_VERSION ="2019-10-11:1432"
import socket
import struct
import network
from network import LoRa
import time
import pycom
from network import WLAN      # For operation of WiFi network
from umqtt import MQTTClient  # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Needed to run any MicroPython code
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
import struct
import socket
import json
m = {'id': 2, 'name': 'markus'}
n = json.dumps(m)
o = json.loads(n)
#print(o['id'], o['name'])
#print(m['name'])

pycom.heartbeat(False) # disable the blue blinking

# A basic package header
# B: 1 byte for the deviceId
# B: 1 byte for the pkg size
# B: 1 byte for the messageId
# %ds: Formated string for string
_LORA_PKG_FORMAT = "!BBB%ds"
_LORA_PKG_FORMAT2= "%ds"
# A basic ack package
# B: 1 byte for the deviceId
# B: 1 byte for the pkg size
# B: 1 byte for the messageId
# B: 1 byte for the Ok (200) or error messages
_LORA_PKG_ACK_FORMAT = "BBBB"

# Let the world know we're starting up.
colorblue = 0x00000F
colorgreen= 0x000F00
colorred  = 0x0F0000

print("Starting LoRaNanoGateway - version:"+_VERSION)
# FUNCTIONS

# Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):          # sub_cb means "callback subroutine"
    print((topic, msg))          # Outputs the message that was received. Debugging use.
    if msg == b"ON":             # If message says "ON" ...
        pycom.rgbled(0xf00000)   # ... then LED on
    elif msg == b"OFF":          # If message says "OFF" ...
        pycom.rgbled(0x000000)   # ... then LED off
    else:                        # If any other message is received ...
        print("Unknown message") # ... do nothing but output that it happened.

def random_integer(upper_bound):
    return machine.rng() % upper_bound

# Open a Lora Socket, use rx_iq to avoid listening to our own messages
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915,frequency=915000000,public=False)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)
pycom.rgbled(0x000101)
time.sleep(1)
pycom.rgbled(0x000000)
# WIFI
# We need to have a connection to WiFi for Internet access
# Code source: https://docs.pycom.io/chapter/tutorials/all/wlan.html
# Wireless network
oWIFI_SSID="STEAM Wifi"
oWIFI_PASS="workBOARDgoodbye95"
WIFI_SSID="vanishinglake"
WIFI_PASS="2Fast4You"
print("Try to connect to wifi "+WIFI_SSID)
wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, auth=(WLAN.WPA2, WIFI_PASS), timeout=5000)

while not wlan.isconnected():    # Code waits here until WiFi connects
    machine.idle()

print("Connected to Wifi")
print(wlan.ifconfig()   )
pycom.rgbled(0xf0d0000) # Status orange: partially working
time.sleep(1)
pycom.rgbled(0x000000)

# Use the MQTT protocol to connect to Bluemix
print("Try to connect to IBM iot")
myiotorg="5q6gu4"
client = MQTTClient("d:"+myiotorg+":playbulb:playbulb30", myiotorg+".messaging.internetofthings.ibmcloud.com",port=1883,user="use-token-auth", password="playbulb30")
#client = MQTTClient(“d:<ORG Id>:<Device Type>:<Device Id>“, “<ORG Id>.messaging.internetofthings.ibmcloud.com”,user=”use-token-auth”, password=”<TOKEN>“, port=1883)
#print(client)
# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
#client.subscribe(AIO_CONTROL_FEED)
#print("Connected to %s, subscribed to %s topic" % (AIO_SERVER, AIO_CONTROL_FEED))
print("Connected to Bluemix")
pycom.rgbled(0x00f000) # Status green: online to Bluemix
#Publish a Hallo
print("Send a Hello to Bluemix")
client.publish(topic="iot-2/evt/random/fmt/json", msg='{"id":'+ubinascii.hexlify(network.LoRa().mac()).decode("utf-8")+',"value":"hello","type":"GW","msgid": -1}' )
#client.publish(topic="iot-2/evt/random/fmt/json", msg='{"id": 0, "h": 0, "t": 0, "ot":0, "w":0, "ts":0, "type":"GW","msgid": -1}' )
try:
    while (True):
        pycom.rgbled(0x000000)
        # Since the maximum body size in the protocol is 255 the request is limited to 512 bytes
        recv_pkg = lora_sock.recv(512)
        if (len(recv_pkg) >4 and len(recv_pkg) < 150):
            print("Received message, length = %d" % len(recv_pkg))
            #print(recv_pkg.decode("utf-8"))
            #a = bytearray(recv_pkg)
            #print(len(a))
            #Remove the byte pakc unpack could be used 2
            b= recv_pkg[4:]
            print("Received a message: %s" % b)
            db=b.decode("utf-8")

            o = json.loads(db)
            print(o['id'])
            o['type']="dev"
            o['gwid']=ubinascii.hexlify(network.LoRa().mac()).decode("utf-8")
            #print(o)
            c=json.dumps(o)
            print(c)
            if o['id'] == 10:
               print("publish node msg to cloud ")
               client.publish(topic="iot-2/evt/random/fmt/json", msg=c )
               pycom.rgbled(colorgreen)  # green
               time.sleep(1)
            else:
                print("Error -- Only Device 10 - Wrong device id =" + str(o['id']))
                pycom.rgbled(colorred)  # green
                time.sleep(1)
            # Unpack the message based on the protocol definition
    #        msg = struct.unpack(_LORA_PKG_FORMAT2 % recv_pkg_len, recv_pkg)
    #        print(msg)
        # If at least a message with the header is received process it
        # for loPy to LoPy


        if (len(recv_pkg) > 200):
            print("<<<<<<<<<<<<< Received INVALID message, length = %d" % len(recv_pkg))
            pycom.rgbled(0x001100)
            recv_pkg_len = recv_pkg[1]
            print(recv_pkg)
            # If message is corrupted should not continue processing
            if (not len(recv_pkg) == recv_pkg_len + 3):
                continue

            # Unpack the message based on the protocol definition
            device_id, pkg_len, msg_id, msg = struct.unpack(_LORA_PKG_FORMAT % recv_pkg_len, recv_pkg)

            # Respond to the device with an acknowledge package
            # time.sleep(0.15)
            print("+++ Received a message: %s" % msg)
            ack_pkg = struct.pack(_LORA_PKG_ACK_FORMAT, device_id, 1, msg_id, 200)
            print("------ Sending an ACK")
            lora_sock.send(ack_pkg)
            print("publish to cloud")
            client.publish(topic="iot-2/evt/random/fmt/json", msg=msg )
            #msg="{\"value\":"+str(some_number)+"}")
            pycom.rgbled(colorgreen)  # green
            time.sleep(1)
            # Do any extra processing required for the package. Keep in mind it should be as fast as posible
            # to make sure that the other clients are not waiting too long for their messages to be ac
except ValueError:
  print(ValueError)
  pycom.rgbled(0x0F0000)
  print("--------------------- An exception occurred(1) ! ---------------------")
  machine.reset()


except:
  pycom.rgbled(0x0F0000)
  print("--------------------- An exception occurred(2) ! ---------------------")
#  machine.reset()
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wlan.disconnect()
    wlan = None
    pycom.rgbled(0x000022)# Status blue: stopped
    print("Disconnected from Bluemix")
