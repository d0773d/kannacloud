import asyncio
import board
import busio
import time
import os
import sys
import json

from multiprocessing import Process

from ezo_sensors import Initialize, Ezo
from nextion import Nextion

# instantiate the objects
init = Initialize()
nextion = Nextion()
ezo = Ezo()

def monitor_nextion():
    while True:
        nextion.monitor_nextion()

def poll_sensors(triggers_actions):
    # Load JSON data
    parsed_data = triggers_actions

    # Dynamically create dictionaries
    sensor_types_dict = {}
    action_dict = {}

    # Iterate through triggers
    for trigger in parsed_data['triggers']:
        for sensor_type, triggers_list in trigger.items():
            if sensor_type not in sensor_types_dict:
                sensor_types_dict[sensor_type] = []
            
            for trigger_info in triggers_list:
                action_name = trigger_info['action_name']
                sensor_types_dict[sensor_type].append(action_name)
                
                # Create dictionary for action
                action_dict[action_name] = parsed_data['actions'][0][action_name]

    # Specify the sensor type and sensor value to check
    sensor_type_to_check = 'pH'
    sensor_value_to_check = 5.5

    # Check if the sensor value for the given sensor type is in the trigger and execute the corresponding action
    if sensor_type_to_check in parsed_data['triggers'][0]:
        for trigger_info in parsed_data['triggers'][0][sensor_type_to_check]:
            if trigger_info['value'] == sensor_value_to_check:
                action_name_to_execute = trigger_info['action_name']
                action_to_execute = action_dict[action_name_to_execute]
                
                '''print(f"Executing action for sensor type '{sensor_type_to_check}', value '{sensor_value_to_check}':")
                print(action_to_execute)'''

                #print(action_dict[action_name_to_execute])
            
                # Check if relay exists in the action_dict
                if action_name_to_execute in action_dict and 'relay' in action_dict[action_name_to_execute][0]:
                    action_to_execute = action_dict[action_name_to_execute][0]['relay']
                        
                    print(f"Executing action for sensor type '{sensor_type_to_check}', value '{sensor_value_to_check}':")
                    print(action_to_execute)
                else:
                    print(f"No relay found for action '{action_name_to_execute}'")

                # Check if print_debug exists in the action_dict
                if action_name_to_execute in action_dict and 'print_debug' in action_dict[action_name_to_execute][0]:
                    action_to_execute = action_dict[action_name_to_execute][0]['print_debug']
                        
                    #print(f"Executing action for sensor type '{sensor_type_to_check}', value '{sensor_value_to_check}':")
                    print(action_to_execute['message'])

    while True:
        print()
        #print(triggers_actions["triggers"]["pH"])
        ezo.poll_sensors(ezo.get_sensor_types_addresses())

triggers_actions = ezo.get_triggers_and_actions()

if init.init_status() is False:
    print("Grab Sensors and Sensor Settings")
    init.initialize_devices()
else:
    print("Initialize: ", True)

# Create a new process with a specified function to execute.
uart_monitor = Process(target=monitor_nextion)
poll_sensors = Process(target=poll_sensors, args=(triggers_actions,))

# Run the new process
#uart_monitor.start()
poll_sensors.start()

while True:
    time.sleep(15)

    if poll_sensors.is_alive():
        print("Alive")
    else:
        #Restart the script if poll_sensors isn't alive.

        os.execv(sys.executable, ['python3'] + sys.argv)
