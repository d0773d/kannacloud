]import asyncio
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
    # Create a dictionary dynamically based on sensor type
    sensor_dict = {}

    # Iterate through triggers
    for trigger in triggers_actions['triggers']:
        for sensor_type, triggers_list in trigger.items():
            for trigger_info in triggers_list:
                action_name = trigger_info['action_name']
                value = trigger_info['value']
                
                # Create dictionary dynamically based on sensor type
                if sensor_type not in sensor_dict:
                    sensor_dict[sensor_type] = {}
                
                sensor_dict[sensor_type][value] = action_name

    # Print the created dictionary
    print("Sensor Dictionary:", sensor_dict)
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
