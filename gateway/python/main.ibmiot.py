# https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/example_sub_led.py
from network import LoRa
from network import WLAN      # For operation of WiFi network
import time                   # Allows use of time.sleep() for delays
import pycom                  # Base library for Pycom devices
from umqtt import MQTTClient  # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Needed to run any MicroPython code
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
import struct
import socket






# BEGIN SETTINGS
# These need to be change to suit your environment
RANDOMS_INTERVAL = 6000 # milliseconds
RANDOMS_INTERVAL_LORA = 5000 # milliseconds
last_random_sent_ticks = 0  # milliseconds
last_random_sent_ticks_lora = 0
# Wireless network
SNP_WIFI_SSID="STEAM Wifi"
SNP_WIFI_PASS="workBOARDgoodbye95"
WIFI_SSID="vanishinglake"
WIFI_PASS="2Fast4You"

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "EngineeringClass79"
AIO_KEY = "1668b943831e4c4eb12b91734f3e3311"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything

AIO_CONTROL_FEED = "EngineeringClass79/feeds/lights"
AIO_RANDOMS_FEED = "EngineeringClass79/feeds/randoms"
AIO_LORANODE_B_FEED = "EngineeringClass79/feeds/lora_node_b"
AIO_LORANODE_C_FEED = "EngineeringClass79/feeds/lora_node_c"

#IBM import
AIO_SERVER = "eahfvb.messaging.internetofthings.ibmcloud.com"
AIO_PORT = 1883
AIO_USER = "token"
AIO_KEY = "playbulb01"
AIO_CLIENT_ID = "d:eahfvb:playbulb:playbulb01"  # Can be anything

#  "org": "eahfvb",
#  "domain": "internetofthings.ibmcloud.com",
#  "type": "playbulb",
#  "id": "playbulb01",
#  "auth-method" : "token",
#  "auth-token" : "playbulb01"
#client = MQTTClient(“d:eahfvb:playbulb:playbulb01“, “eahfvb.messaging.internetofthings.ibmcloud.com”,user=”use-token-auth”, password=”playbulb01“, port=1883)

# END SETTINGS
print("Starting lora-to-mqtt v2")
# RGBLED
# Disable the on-board heartbeat (blue flash every 4 seconds)
# We'll use the LED to respond to messages from Adafruit IO
pycom.heartbeat(False)
time.sleep(0.1) # Workaround for a bug.
                # Above line is not actioned if another
                # process occurs immediately afterwards
pycom.rgbled(0xf00000)  # Status red = not working

# WIFI
# We need to have a connection to WiFi for Internet access
# Code source: https://docs.pycom.io/chapter/tutorials/all/wlan.html

wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, auth=(WLAN.WPA2, WIFI_PASS), timeout=5000)

while not wlan.isconnected():    # Code waits here until WiFi connects
    machine.idle()

print("Connected to Wifi")
print(wlan.ifconfig()   )
pycom.rgbled(0xf0d0000) # Status orange: partially working

# Lora Setup
pycom.heartbeat(False)
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915,frequency=915000000,public=False)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)
print("LoPy A v0.3")
colorblue = 0x00000F
colorgreen= 0x000F00
color = colorgreen
pycom.rgbled(0x00d0000) # Status gree

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

def send_random():
    global last_random_sent_ticks
    global RANDOMS_INTERVAL

    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        return; # Too soon since last one sent.


    some_number = random_integer(100)
    if (some_number  > 50):
        color=colorblue
    else:
        color=colorgreen
    s.send("HelloFromGWimport os")
    AIO_RANDOMS_FEED="iot-2/evt/random/fmt/json"
    print("Publishing: {0} to {1} ... ".format(some_number, AIO_RANDOMS_FEED), end='')
    try:
        client.publish(topic="iot-2/evt/random/fmt/json", msg="{\"value\":"+str(some_number)+"}")
#        client.publish(topic=AIO_RANDOMS_FEED, msg=str(some_number))
        pycom.rgbled(color)  # green

        print("DONE")
    except Exception as e:
        print("FAILED")
        print(e)
        pycom.rgbled(0x550000)  # yellow
    finally:
        last_random_sent_ticks = time.ticks_ms()

def send_loranodevalue(devid,value):
    global last_random_sent_ticks_lora
    global RANDOMS_INTERVAL_LORA
    pycom.rgbled(colorblue)  # Blue
    if ((time.ticks_ms() - last_random_sent_ticks_lora) < RANDOMS_INTERVAL_LORA):
        return; # Too soon since last one sent
    feed =  AIO_LORANODE_B_FEED
    if(devid == "B"):
        feed =  AIO_LORANODE_B_FEED
    if(devid == "C"):
        feed =  AIO_LORANODE_C_FEED
    some_number = value
    print("Publishing: {0} to {1} ... ".format(some_number, feed), end='')
    try:
        client.publish(topic=feed, msg=str(some_number))
        print("DONE-"+str(devid)+"-"+str(some_number))
        pycom.rgbled(0x000f00)  # green
    except Exception as e:
        pycom.rgbled(0xf00000)  # red
        print("FAILED")
    finally:
        last_random_sent_ticks_lora = time.ticks_ms()


# Use the MQTT protocol to connect to Adafruit IO
print("Try to connect to IBM iot")
#client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)
client = MQTTClient("d:5q6gu4:playbulb:playbulb01", "5q6gu4.messaging.internetofthings.ibmcloud.com",port=1883,user="use-token-auth", password="playbulb01")
#client = MQTTClient(“d:<ORG Id>:<Device Type>:<Device Id>“, “<ORG Id>.messaging.internetofthings.ibmcloud.com”,user=”use-token-auth”, password=”<TOKEN>“, port=1883)
print(client)
# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
#client.subscribe(AIO_CONTROL_FEED)
print("Connected to %s, subscribed to %s topic" % (AIO_SERVER, AIO_CONTROL_FEED))

pycom.rgbled(0x00f000) # Status green: online to Adafruit IO

try:                      # Code between try: and finally: may cause an error
                          # so ensure the client disconnects the server if
                          # that happens.
    while True:              # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
        send_random()     # Send a random number to Adafruit IO if it's time.
        data =s.recv(64)

        if "Ping" in data:
            print(data)
            substr = data[9:len(data)].decode('utf-8') #'PingLoPyB5996'
            devid = data[8:9].decode('utf-8') #'PingLoPyB5996'
            print(devid)
            send_loranodevalue(devid,substr)
            print(substr)
            print(">>>>> Yeah LoPy A >> got PING message >>> sending PONG ")
            s.send("Pong")


finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wlan.disconnect()
    wlan = None
    pycom.rgbled(0x000022)# Status blue: stopped
    print("Disconnected from Bluemix IoT.")
