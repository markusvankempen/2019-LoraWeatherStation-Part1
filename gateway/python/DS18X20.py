#!/usr/bin/env python
#
#### DS18X20 and Soile moiture
#

import time
import pycom
from machine import Pin
from onewire import DS18X20
from onewire import OneWire
pycom.heartbeat(False)
print("DS18X20")
#DS18B20 data line connected to pin P10
ow = OneWire(Pin('P10'))
temp = DS18X20(ow)
# make `P10` an input with the pull-up enabled
p_in = Pin('P13', mode=Pin.IN, pull=Pin.PULL_DOWN)
p_in() # get value, 0 or 1
print(p_in())

adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P16')   # create an analog pin on P16
val = apin()

while True:
    temp.start_conversion()
    time.sleep(1)
    print(temp.read_temp_async())
    print(p_in())
    apin = adc.channel(pin='P16')   # create an analog pin on P16
    val = apin()
    print(val )
    time.sleep(1)
