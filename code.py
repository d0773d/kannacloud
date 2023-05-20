import board
import busio
import time

from ezo_sensors import Ezo
# from adafruit_ht16k33.segments import Seg7x4

# instantiate the object
humidity = Ezo(0x6F, False)

while True:
    time.sleep(5)
    print("test2")

    # call our instance methods
    # humidity.cmd_enable_all_paramaters()
    # humidity.cmd_set_name()

    humidity.cmd_r()
