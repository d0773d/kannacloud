import board
import busio
import time

class Ezo:
    # instance attribute
    def __init__(self, i2c_addr, seven_seg_output=False, touch_scr_output=False):
        from adafruit_bus_device.i2c_device import I2CDevice

        self.ezo_sensor_settings = {
            "device_address": i2c_addr,
            "short_wait": 3,
            "long_wait": 5,
            "largest_string": 24,
            "smallest_string": None,
            "name": None,
            "units": None
        }

        self.ezo_sensor_values = {
            "result": bytearray(24)
        }

        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Create library object on our I2C port
        self.device = I2CDevice(self.i2c, i2c_addr)

    def cmd_set_name(self):
        cmd = "Name,hum1"

        # Encode cmd variable to a bytearray
        cmd = cmd.encode()

        time.sleep(3)

        # Set the result buffer with the Sensor data result
        with self.device:
            self.device.write(cmd)

    def cmd_enable_all_paramaters(self):
        # Send O,Dew,1 command
        # Enables all the parameters

        cmd = "O,Dew,1"

        # Encode cmd variable to a bytearray
        cmd = cmd.encode()

        time.sleep(3)

        # Set the result buffer with the Sensor data result
        with self.device:
            self.device.write(cmd)

    def cmd_r(self):
        # Send the R command

        cmd = "R"

        # Encode cmd variable to a bytearray
        cmd = cmd.encode()

        time.sleep(3)

        # Set the result buffer with the Sensor data result
        with self.device:
            self.device.write(cmd)

        # EZO sensor needs a delay to calculate the result
        time.sleep(self.ezo_sensor_settings["long_wait"])

        # Set the result buffer with the Sensor data result
        with self.device:
            raw_result = bytearray(self.ezo_sensor_settings["largest_string"])
            self.device.readinto(raw_result)

            if raw_result[0] == 1:             # if the response isn't an error
                # Convert bytearray to string
                str_result = ''.join([chr(b) for b in raw_result])

                # remove first char of 1
                str_result = str_result[1:]

                #remove \x00 from the end of the string
                str_result = str_result.replace('\x00','')
                print(str_result)
            else:
                # Output the response value if it is anything other than a 1
                print("ERROR")
                #print(str(response[0]))

        '''if len(self.result) != 0:
            self.env_temp = self.result.split(',')[1]
            self.env_humidity = self.result.split(',')[0]'''
