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
    # Given sensor type and value
    given_sensor_type = "RTD"  # Replace with the sensor type you're looking for
    given_value = 79  # Replace with the value you're looking for

    # Find the corresponding action name
    action_name = None

    # Iterate through triggers
    for trigger in triggers_actions['triggers']:
        if given_sensor_type in trigger:
            for trigger_info in trigger[given_sensor_type]:
                if trigger_info['value'] == given_value:
                    action_name = trigger_info['action_name']
                    break

    # Print the result
    if action_name is not None:
        print(f"Action Name for {given_sensor_type} value {given_value}: {action_name}")
    else:
        print(f"No action found for {given_sensor_type} value {given_value}")

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
