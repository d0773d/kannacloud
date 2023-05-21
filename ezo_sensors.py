import board
import busio
import time

from adafruit_bus_device.i2c_device import I2CDevice
i2c = busio.I2C(board.SCL, board.SDA)

class Ezo:
    # instance attribute
    def __init__(self, i2c_addr, sensor_type, seven_seg_output=False, touch_scr_output=False):
        #print(sensor_type)
        # Create library object on our I2C port
        self.device = I2CDevice(i2c, i2c_addr)

        self.ezo_sensor_settings = {
            "device_address": i2c_addr,
            "sensor_type": sensor_type,
            "short_wait": 3,
            "long_wait": 5,
            "largest_string": 24,
            "smallest_string": 4,
            "name": None,
            "units": None
        }

        self.ezo_sensor_values = {
            "result": bytearray(24),
            "relative_humidity": None,
            "dew_point": None,
            "air_temperature": None
        }

    def cmd_set_phplock(self):
        cmd = "Plock,1"
        
        # Encode cmd variable to a bytearray
        cmd = cmd.encode()

        time.sleep(3)

        # Set the result buffer with the Sensor data result
        with self.device:
            self.device.write(cmd)

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

            # if the response isn't an error
            if raw_result[0] == 1:
                # Convert bytearray to string
                str_result = ''.join([chr(b) for b in raw_result])

                # remove first char of 1
                str_result = str_result[1:]

                #remove \x00 from the end of the string
                str_result = str_result.replace('\x00','')

                if self.ezo_sensor_settings["sensor_type"] == "hum":
                    # Populate humidity sensor values
                    self.ezo_sensor_values["relative_humidity"] = str_result.split(',')[0]
                    self.ezo_sensor_values["air_temperature"] = str_result.split(',')[1]
                    self.ezo_sensor_values["dew_point"] = str_result.split(',')[3]

                    #print(str_result)
                    print("Relative Humidity: ", self.ezo_sensor_values["relative_humidity"])
                    print("Air Temperature: ", self.ezo_sensor_values["air_temperature"])
                    print("Dew Point: ", self.ezo_sensor_values["dew_point"])
                
                if self.ezo_sensor_settings["sensor_type"] == "tmp":
                    #print("Res Temp")
                    print("Reservoir Temperature: ", str_result)
                    
                if self.ezo_sensor_settings["sensor_type"] == "ph":
                    print("pH Value: ", str_result)
            else:
                print("ERROR")
