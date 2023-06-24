import asyncio
import board
import busio
import time

from multiprocessing import Process
from multiprocessing import Value

from ezo_sensors import Initialize, Ezo
from nextion import Nextion
    
# function executed in child process
def monitor_nextion():
    while True:
        time.sleep(1)
        nextion.monitor_nextion()

def poll_sensors(devices):
    while True:
        time.sleep(1)
        ezo.poll_sensors(devices)

if __name__ == '__main__':
    loop_sensors = False

    device_dict = []

    init = Initialize()
    nextion = Nextion()
    ezo = Ezo()

    if not init.init_status():
        init.initialize_devices()
        time.sleep(2)

        init.update_settings_file("settings", True, "init")

    if init.init_status():
        print("Initialize: ", True)

        device_dict = ezo.get_sensor_types_addresses()

        # configure a child process to run the task
        uart_monitor = Process(target=monitor_nextion)
        sensors = Process(target=poll_sensors, args=(device_dict,))

        uart_monitor.start()
        sensors.start()

    while True:
        time.sleep(10)
        print("While loop!!!!!!!!")
        loop_sensors = False

        if not loop_sensors:
            uart_monitor.terminate()
            sensors.terminate()

            uart_monitor.join()
            sensors.join()

        loop_sensors = True

        time.sleep(10)

        if loop_sensors:
            uart_monitor = Process(target=monitor_nextion)
            sensors = Process(target=poll_sensors, args=(device_dict,))

            uart_monitor.start()
            sensors.start()
