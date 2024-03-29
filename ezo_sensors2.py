import board
import busio
import time
import json

from nextion import Nextion
from adafruit_bus_device.i2c_device import I2CDevice

i2c = busio.I2C(board.SCL, board.SDA)
nextion = Nextion()

class Initialize:
    def __init__(self, ezo_instance):
        self.ezo_instance = ezo_instance

        if not self.init_status():
            self.initialize_devices()
        elif self.init_status():
            self.ezo_instance.populate_ezo_settings_i2c()

        print("Initializing")

    def init_status(self):
        # Opening JSON file
        with open('/home/pi/code/python/kc_settings.json', 'r') as f:
            # returns JSON object as 
            # a dictionary
            json_data = json.load(f)
 
        # Closing file
        f.close()

        return json_data['settings'][0]['init']

    def update_settings_file(self, key, value, subkey=None):
        jsonFile = open("/home/pi/code/python/kc_settings.json", "r") # Open the JSON file for reading
        settings_file = json.load(jsonFile) # Read the JSON into a buffer
        jsonFile.close() # Close the JSON file

        if subkey is not None:
            settings_file[key][0][subkey] = value
        else:
            settings_file[key].append(value)

        with open('/home/pi/code/python/kc_settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings_file, f, ensure_ascii=False, indent=4)

        f.close() # Close the JSON file

    def initialize_devices(self):
        print("Getting Sensor info")
        json_data = []
        device_list = []

        while not i2c.try_lock():
            pass

        try:
            for device in i2c.scan():
                device_list.append(device)

        finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
            i2c.unlock()

            for device in device_list:
       
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

                            if moduletype == "pH":
                                self.ezo_instance.ezo_sensor_settings["ph_i2c_addr"] = str(device)
                            if moduletype == "RTD":
                                self.ezo_instance.ezo_sensor_settings["rtd_i2c_addr"] = str(device)
                            if moduletype == "HUM":
                                self.ezo_instance.ezo_sensor_settings["hum_i2c_addr"] = str(device)

                            json_str = '{"type": ' + '"' + moduletype + '", "address": ' + str(device) + '}'
                            json_formated_data = json.loads(json_str)

                            self.update_settings_file("sensors", json_formated_data)

            self.update_settings_file("settings", True, "init")

class Ezo:
    # instance attribute
    def __init__(
            self,
            seven_seg_output=False,
            touch_scr_output=False,
        ):

        self.app_settings = {
            "manual_mode": False
        }

        self.ezo_sensor_settings = {
            "short_wait": 0.8,
            "long_wait": 5,
            "ph_cal_wait": 0.9,
            "ec_cal_wait": 0.6,
            "largest_string": 24,
            "smallest_string": 4,
            "ph_i2c_addr": None,
            "rtd_i2c_addr": None,
            "hum_i2c_addr": None,
            "poll_sensors": True,
            "ph_calibrate": False,
            "ec_calibrate": False
        }

        self.ezo_sensor_values = {
            "result": bytearray(24),
            "res_temp": None,
            "pH": None,
            "relative_humidity": None,
            "dew_point": None,
            "air_temperature": None
        }

    def get_triggers_and_actions(self):
        # Opening JSON file
        with open('/home/pi/code/python/triggers_actions.json', 'r') as f:
            # returns JSON object as 
            # a dictionary
            json_data = json.load(f)
 
        # Closing file
        f.close()

        if all(key in json_data for key in ("triggers", "actions")):
            if len(json_data["triggers"]) and len(json_data["actions"]) != 0:
                #print("Triggers and Actions are found")
                return json_data
        else:
            return None
            
    def run_triggers_actions(self, triggers_actions, sensor_type, sensor_value):
        # Set the current_sensor_type variable with the current sensor_type attribute value
        # This is needed due to a bug where it will get stuck on a 
        # sensor_type value during the Iterate through triggers code below starting at code line #147
        current_sensor_type_value = sensor_type

        # Load JSON data
        parsed_data = triggers_actions
        
        # Dynamically create dictionaries
        sensor_types_dict = {}
        action_dict = {}

        # Iterate through triggers
        for trigger in parsed_data['triggers']:
            for sensor_type, triggers_list in trigger.items():
                sensor_type = current_sensor_type_value
                if sensor_type not in sensor_types_dict:
                    sensor_types_dict[sensor_type] = []
                
                for trigger_info in triggers_list:
                    action_name = trigger_info['action_name']
                    sensor_types_dict[sensor_type].append(action_name)
                    
                    # Create dictionary for action
                    action_dict[action_name] = parsed_data['actions'][0][action_name]

        # Debug run_trigger_actions function by specifying the sensor type and sensor value to check
        #sensor_type_to_check = 'pH'
        #sensor_value_to_check = 5.5

        sensor_type_to_check = current_sensor_type_value

        #convert sensor_value to a float so you can check the float sensor value in triggers_actions.json file
        sensor_value_to_check = float(sensor_value)

        # Check if the sensor value for the given sensor type is in the trigger and execute the corresponding action
        if sensor_type_to_check in parsed_data['triggers'][0]:
            for trigger_info in parsed_data['triggers'][0][sensor_type_to_check]:
                if trigger_info['value'] == sensor_value_to_check:
                    action_name_to_execute = trigger_info['action_name']
                    action_to_execute = action_dict[action_name_to_execute]
                
                    # Check if relay exists in the action_dict
                    if action_name_to_execute in action_dict and 'relay' in action_dict[action_name_to_execute][0]:
                        action_to_execute = action_dict[action_name_to_execute][0]['relay']
                            
                        print(f"Executing action for sensor type '{sensor_type}', value '{sensor_value_to_check}':")
                        print(action_to_execute)
                    else:
                        print(f"No relay found for action '{action_name_to_execute}'")

                    # Check if print_debug exists in the action_dict
                    if action_name_to_execute in action_dict and 'print_debug' in action_dict[action_name_to_execute][0]:
                        action_to_execute = action_dict[action_name_to_execute][0]['print_debug']

                        print(action_to_execute['message'])

    def populate_ezo_settings_i2c(self):
        poll_sensor_list = self.get_sensor_types_addresses()

        for sensor in poll_sensor_list:
            sensor_type = sensor['type']
            sensor_address = sensor['address']

            if sensor_type == "pH":
                self.ezo_sensor_settings["ph_i2c_addr"] = sensor_address

            if sensor_type == "RTD":
                self.ezo_sensor_settings["rtd_i2c_addr"] = sensor_address

            if sensor_type == "HUM":
                self.ezo_sensor_settings["hum_i2c_addr"] = sensor_address
            
            #print(f"Sensor Type: {sensor_type}, Address: {sensor_address}")

    def get_sensor_types_addresses(self):
        # Opening JSON file
        with open('/home/pi/code/python/kc_settings.json', 'r') as f:
            # returns JSON object as 
            # a dictionary
            json_dict = json.load(f)

        # Closing file
        f.close()

        return json_dict["sensors"]
    
    def calibrate_ph(self, i2c_addr, cal_type):
        i2c_address = None

        if cal_type == "mid":
            #self.send_sensor_cmd(i2c_address, "Cal,mid,7.00")
            print("mid point calibration at address:", i2c_addr)

        if cal_type == "low":
            print()
            #self.send_sensor_cmd(i2c_address, "Cal,low,4.00")
        
        if cal_type == "high":
            print()
            #self.send_sensor_cmd(i2c_address, "Cal,high,10.00")

    def send_sensor_cmd(
            self,
            i2c_addr,
            sensor_type=None,
            command=None,
            triggers_actions=None,
            cal_mode=None):
        # Set cmd variable to encode the sensor command to a byte array
        cmd = None
        
        # Set the current Res temp to current_res_temp variable to use for temp compensated sensor values
        current_res_temp = self.ezo_sensor_values["res_temp"]

        # pH reading should only be temperature compensated so...
        # Code should skip the first pH reading because ezo_sensor_values["res_temp"] should be None; however,
        # this depends on how the initialize code gets the sensor address and stores them in the kc_settings.json file
        #
        # Code should get the next pH reading because ezo_sensor_values["res_temp"] should be set with the current res temp value
        if current_res_temp != None and cal_mode != True and sensor_type == "pH":
            #print("current_res_temp variable is NOT None")
            cmd = "RT," + current_res_temp

            # Encode cmd variable to a bytearray
            cmd = cmd.encode()
        elif cal_mode == True and sensor_type == "pH":
            cmd = "R"

            cmd = cmd.encode()

        if sensor_type == "RTD" or sensor_type == "HUM":
            cmd = "R"

            # Encode cmd variable to a bytearray
            cmd = cmd.encode()
    
        if cmd is not None:
            #print("current_res_temp: ", current_res_temp)

            # Create library object on our I2C port
            self.device = I2CDevice(i2c, i2c_addr)

            # Send the R command
            # Set the result buffer with the Sensor data result
            #print("BEFORE running write command cmd variable value ", cmd)
            with self.device:
                self.device.write(cmd)

            # EZO sensor needs a delay to calculate the result
            if cal_mode:
                time.sleep(self.ezo_sensor_settings["ph_cal_wait"])
            else:
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

                    if sensor_type == "pH":
                        # Converting str_result to a float and formatting it to one decimal point, then set the str_result var to str_result
                        
                        #str_result = "{:.1f}".format(float(str_result))

                        # Send pH value to the nextion screen
                        if cal_mode == False:
                            str_result = str_result[:-2]

                            # Populate the pH value to the self.ezo_sensor_values dictionary
                            self.ezo_sensor_values["pH"] = str_result

                            # Output the sensor value to the terminal
                            print("pH Value: ", str_result)

                            # Execute the run_triggers_actions function
                            self.run_triggers_actions(triggers_actions, "pH", str_result)

                            nextion.nextion_send_value("ph", str_result)
                        elif cal_mode == True:
                            nextion.nextion_send_value("phcal", str_result)
                        print()

                    if sensor_type == "HUM":
                        # Populate humidity sensor values to the self.ezo_sensor_values dictionary
                        self.ezo_sensor_values["relative_humidity"] = str_result.split(',')[0]
                        self.ezo_sensor_values["air_temperature"] = str_result.split(',')[1]
                        self.ezo_sensor_values["dew_point"] = str_result.split(',')[3]

                        # Output the sensor values to the terminal
                        print("Relative Humidity: ", self.ezo_sensor_values["relative_humidity"])
                        print("Air Temperature: ", self.ezo_sensor_values["air_temperature"])
                        print("Dew Point: ", self.ezo_sensor_values["dew_point"])

                        nextion.nextion_send_value("humidity", self.ezo_sensor_values["relative_humidity"])
                        time.sleep(1)
                        nextion.nextion_send_value("airtemp", self.ezo_sensor_values["air_temperature"])
                        time.sleep(1)
                        nextion.nextion_send_value("dewpoint", self.ezo_sensor_values["dew_point"])
                        time.sleep(1)

                        print()

                    if sensor_type == "RTD":
                        str_result = "{:.1f}".format(float(str_result))

                        # Populate the Reservoir Temperature value to the self.ezo_sensor_values dictionary
                        self.ezo_sensor_values["res_temp"] = str_result

                        # Output the sensor value to the terminal
                        print("Reservoir Temperature: ", str_result)
                        
                        # Execute the run_triggers_actions function
                        self.run_triggers_actions(triggers_actions, "RTD", str_result)

                        nextion.nextion_send_value("rtd", str_result)

                        print()
                else:
                    print("ERROR")
