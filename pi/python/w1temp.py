import time
from w1thermsensor import W1ThermSensor
sensor = W1ThermSensor()
#sensor.gpio=3
while True:
 #   temperature = sensor.get_temperature()
#@    print("The temperature is %s celsius" % temperature)
#    print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
    time.sleep(1)
    for sensor in W1ThermSensor.get_available_sensors():
        print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
    print("...")
