import asyncio
import board
import busio
import time

from multiprocessing import Process
from multiprocessing import Value

from ezo_sensors import Initialize, Ezo
from nextion import Nextion
    
# function executed in child process
def monitor_nextion(custom):
    while True:
        time.sleep(2)
        print("loop_sensors is", loop_sensors)
        if loop_sensors:
            nextion.monitor_nextion()

def poll_sensors(custom):
    while True:
        time.sleep(1)
        print("READY: ", loop_sensors)
        print(loop_sensors)

        if loop_sensors:
            ezo.poll_sensors(ezo.get_sensor_types_addresses())

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

        loop_sensors = True

        device_dict = ezo.get_sensor_types_addresses()

        # configure a child process to run the task
        uart_monitor = Process(target=monitor_nextion, args=(loop_sensors,))

        poll_sensors = Process(target=poll_sensors, args=(loop_sensors,))

        uart_monitor.start()
        #poll_sensors.start()

    while True:
        time.sleep(10)
        print("While loop!!!!!!!!")
        loop_sensors = False

        if not loop_sensors:
            uart_monitor.terminate()
            uart_monitor.join()

        loop_sensors = True

        time.sleep(10)

        if loop_sensors:
            uart_monitor = Process(target=monitor_nextion, args=(loop_sensors,))
            uart_monitor.start()
