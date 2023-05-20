import board
import busio
import time

from ezo_sensors import Ezo

class App:
    def __init__(self, i2c, seven_seg_output=False, touch_scr_output=False):
        self.ezohum = Ezo(i2c, 0x6F)
        self.seven_seg_output = seven_seg_output
        if seven_seg_output:
            from adafruit_ht16k33.segments import Seg7x4
            #self.temp_display = Seg7x4(self.i2c, address=0x71)
            self.humidity_display = Seg7x4(self.i2c, address=0x72)
        self.res_temp = None
        self.res_ph = None
        self.res_ec = None

    def send_result_to_7seg(self):
        print(len(self.ezohum.humidity))
        #self.humidity_display.print('0123')
        #self.temp_display.print(self.ezohum.temperature)
        self.humidity_display.print(self.ezohum.humidity)

    def cmd_r(self):
        # retrieve the EZO-HUM data
        self.ezohum.update_data()
        # update the displays
        if self.seven_seg_output:
            self.send_result_to_7seg()