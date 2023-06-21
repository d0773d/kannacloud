import asyncio
import board
import busio
import time

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

def poll_sensors():
    while True:
        ezo.poll_sensors(ezo.get_sensor_types_addresses())

if init.init_status() is False:
    init.initialize_devices()
else:
    print("Initialize: ", True)

    # Create a new process with a specified function to execute.
    uart_monitor = Process(target=monitor_nextion)
    poll_sensors = Process(target=poll_sensors)

    # Run the new process
    uart_monitor.start()
    poll_sensors.start()
