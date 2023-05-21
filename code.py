import board
import busio
import time

from ezo_sensors import Ezo
# from adafruit_ht16k33.segments import Seg7x4

# instantiate the object
humidity = Ezo(0x6F, "hum", False)
res = Ezo(0x66, "tmp", False)
ph = Ezo(0x63, "ph", False)

while True:
    time.sleep(1)

    # call our instance methods
    # humidity.cmd_enable_all_paramaters()
    # humidity.cmd_set_name()
    #ph.cmd_set_phplock()

    humidity.cmd_r()
    time.sleep(1)
    res.cmd_r()
    time.sleep(1)
    ph.cmd_r()
