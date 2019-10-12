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
# BEGIN SETTINGS
# These need to be change to suit your environment
RANDOMS_INTERVAL = 6000 # milliseconds
RANDOMS_INTERVAL_LORA = 5000 # milliseconds
last_random_sent_ticks = 0  # milliseconds
last_random_sent_ticks_lora = 0
# Wireless network
WIFI_SSID="vanishinglake"
WIFI_PASS="2Fast4You"

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "markusvankempen"
AIO_KEY = "c453af28034a44e1bc0a480764de782d"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_CONTROL_FEED = "markusvankempen/feeds/lights"
AIO_RANDOMS_FEED = "markusvankempen/feeds/randoms"
AIO_LORANODE_B_FEED = "markusvankempen/feeds/lora_node_b"
# END SETTINGS
print("Starting lora-to-mqtt v1")
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
lora = LoRa(mode=LoRa.LORA, region=LoRa.US915)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)
print("LoPy A v0.1")
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

    print("Publishing: {0} to {1} ... ".format(some_number, AIO_RANDOMS_FEED), end='')
    try:
        client.publish(topic=AIO_RANDOMS_FEED, msg=str(some_number))
        pycom.rgbled(color)  # green

        print("DONE")
    except Exception as e:
        print("FAILED")
        pycom.rgbled(0xFF00FF)  # yellow
    finally:
        last_random_sent_ticks = time.ticks_ms()

def send_loranodevalue(value):
    global last_random_sent_ticks_lora
    global RANDOMS_INTERVAL_LORA
    pycom.rgbled(colorblue)  # Blue
    if ((time.ticks_ms() - last_random_sent_ticks_lora) < RANDOMS_INTERVAL_LORA):
        return; # Too soon since last one sent

    some_number = value
    print("Publishing: {0} to {1} ... ".format(some_number, AIO_LORANODE_B_FEED), end='')
    try:
        client.publish(topic=AIO_LORANODE_B_FEED, msg=str(some_number))
        print("DONE-"+str(some_number))
        pycom.rgbled(0x000f00)  # green
    except Exception as e:
        pycom.rgbled(0xf00000)  # red
        print("FAILED")
    finally:
        last_random_sent_ticks_lora = time.ticks_ms()


# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)

# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
client.subscribe(AIO_CONTROL_FEED)
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
#            send_loranodevalue(substr)
            print(substr)
            print(">>>>> Yeah LoPy A >> got PING message >>> sending PONG ")
            s.send("Pong")


finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wlan.disconnect()
    wlan = None
    pycom.rgbled(0x000022)# Status blue: stopped
    print("Disconnected from Adafruit IO.")
