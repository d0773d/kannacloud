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

    '''# Print the created dictionaries
    print("Sensor Types Dictionary:", sensor_types_dict)
    print("\nAction Dictionary:")
    for action_name, actions in action_dict.items():
        print(f"{action_name}: {actions}")'''


    print(sensor_types_dict)
    print()
    print(action_dict)

    while True:
        print()
        #print(triggers_actions["triggers"]["pH"])
        ezo.poll_sensors(ezo.get_sensor_types_addresses())

triggers_actions = init.get_triggers_and_actions()

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
