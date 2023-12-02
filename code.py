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

poll_sensor_list = ezo.get_sensor_types_addresses()
triggers_actions = ezo.get_triggers_and_actions()

def monitor_nextion():
    while True:
        nextion.monitor_nextion()

def poll_sensors():
    while True:
        print()
        #print(triggers_actions["triggers"]["pH"])
        ezo.poll_sensors(poll_sensor_list, triggers_actions)

if init.init_status() is False:
    print("Grab Sensors and Sensor Settings")
    init.initialize_devices()
else:
    print("Initialize: ", True)

# Create a new process with a specified function to execute.
uart_monitor = Process(target=monitor_nextion)
poll_sensors = Process(target=poll_sensors)

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
