import board
import busio
import time
import json

from adafruit_bus_device.i2c_device import I2CDevice
i2c = busio.I2C(board.SCL, board.SDA)

class Initialize:
    def __init__(self):
        print("Initializing")

    def init_status(self):
        # Opening JSON file
        with open('kc_settings.json', 'r') as f:
            # returns JSON object as 
            # a dictionary
            jason_data = json.load(f)
 
        # Closing file
        f.close()

        return jason_data['settings'][0]['init']

    def update_settings_file(self, key, value, subkey=None):
        jsonFile = open("kc_settings.json", "r") # Open the JSON file for reading
        settings_file = json.load(jsonFile) # Read the JSON into a buffer
        jsonFile.close() # Close the JSON file

        if subkey is not None:
            settings_file[key][0][subkey] = value
        else:
            settings_file[key].append(value)

        with open('kc_settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings_file, f, ensure_ascii=False, indent=4)

    def initialize_devices(self):
        json_data = []
        device_list = []

        while not i2c.try_lock():
            pass

        try:
            for device in i2c.scan():
                device_list.append(device)
                #print(hex(device_address))

        finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
            i2c.unlock()

            for device in device_list:
                #print(device)

                sensor = I2CDevice(i2c, device)
                
                cmd = 'i'
                cmd = cmd.encode()

                with sensor:
                    sensor.write(cmd)

                time.sleep(.3)

                with sensor:
                    raw_result = bytearray(15)
                    sensor.readinto(raw_result)
                    str_result = ''.join([chr(b) for b in raw_result])
                    # check if the device is an EZO device
                    checkEzo = str_result.split(",")
                    if len(checkEzo) > 0:
                        if checkEzo[0].endswith("?I"):
                            # yes - this is an EZO device
                            moduletype = checkEzo[1]
                            '''json_data.append({
                                "type": moduletype,
                                "address": device
                            })'''

                            json_str = '{"type": ' + '"' + moduletype + '", "address": ' + str(device) + '}'
                            json_formated_data = json.loads(json_str)
                            #json_data.append(json_formated_data)

                            self.update_settings_file("sensors", json_formated_data)

class Ezo:
    # instance attribute
    def __init__(
            self,
            seven_seg_output=False,
            touch_scr_output=False,
            i2c_addr=None,
            sensor_type=None,
        ):
        #print(sensor_type)
        # Create library object on our I2C port
        #self.device = I2CDevice(i2c, i2c_addr)

        self.i2c_addresses = []

        self.ezo_sensor_settings = {
            "device_address": i2c_addr,
            "sensor_type": sensor_type,
            "short_wait": .8,
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

    def get_sensor_types_addresses(self):
        # Opening JSON file
        with open('kc_settings.json', 'r') as f:
            # returns JSON object as 
            # a dictionary
            json_dict = json.load(f)

        # Closing file
        f.close()

        return json_dict["sensors"]

        '''for sensors in json_dict["sensors"]:
            self.i2c_addresses.append(sensors["address"])
        return self.i2c_addresses'''

    def poll_sensors(self, sensors):
        for i in sensors:
            self.cmd_r(i["type"], i["address"])

    def cmd_r(self, sensor_type, i2c_addr):
        # Create library object on our I2C port
        self.device = I2CDevice(i2c, i2c_addr)

        # Send the R command

        cmd = "R"

        # Encode cmd variable to a bytearray
        cmd = cmd.encode()

        #time.sleep(3)

        # Set the result buffer with the Sensor data result
        with self.device:
            self.device.write(cmd)

        # EZO sensor needs a delay to calculate the result
        time.sleep(self.ezo_sensor_settings["short_wait"])

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

                if sensor_type == "HUM":
                    # Populate humidity sensor values
                    self.ezo_sensor_values["relative_humidity"] = str_result.split(',')[0]
                    self.ezo_sensor_values["air_temperature"] = str_result.split(',')[1]
                    self.ezo_sensor_values["dew_point"] = str_result.split(',')[3]

                    #print(str_result)
                    print("Relative Humidity: ", self.ezo_sensor_values["relative_humidity"])
                    print("Air Temperature: ", self.ezo_sensor_values["air_temperature"])
                    print("Dew Point: ", self.ezo_sensor_values["dew_point"])

                if sensor_type == "RTD":
                    #print("Res Temp")
                    print("Reservoir Temperature: ", str_result)
   
                if sensor_type == "pH":
                    print("pH Value: ", str_result)
            else:
                print("ERROR")
