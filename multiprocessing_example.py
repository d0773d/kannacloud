import asyncio
import board
import busio
import time
import os
import sys
import json
import multiprocessing

from ezo_sensors import Initialize, Ezo
from nextion import Nextion

# instantiate the objects
init = Initialize()
nextion = Nextion()
ezo = Ezo()

poll_sensor_list = ezo.get_sensor_types_addresses()
triggers_actions = ezo.get_triggers_and_actions()


def monitor_nextion(queue):
    while True:
        command = nextion.monitor_nextion()

        if command:
            print("From the process:", command[0])
            queue.put(command)
        else:
            print("Command is empty")

        # Add a small delay to avoid excessive CPU usage
        time.sleep(0.1)

def poll_sensors(queue):
    while True:
        print("Still looping")

        print(ezo.ezo_sensor_settings["poll_sensors"])

        if ezo.ezo_sensor_settings["poll_sensors"]:
            ezo.poll_sensors(poll_sensor_list, triggers_actions)

        if not queue.empty():
                command = queue.get(block=False)

                # If message is cmd1, set ezo.ezo_sensor_settings["poll_sensors"] to True
                print("Command: ", command)
                if command and command[0] == "cmd1":
                    ezo.ezo_sensor_settings["poll_sensors"] = True
                
                # If message is cmd2, set ezo.ezo_sensor_settings["poll_sensors"] to False
                if command and command[0] == "cmd2":
                    ezo.ezo_sensor_settings["poll_sensors"] = False

        # Add a small delay to avoid excessive CPU usage
        time.sleep(1)

if __name__ == "__main__":
    # Create a multiprocessing Queue
    message_queue = multiprocessing.Queue()

    # Create the monitor_nextion_process process
    monitor_nextion_process = multiprocessing.Process(target=monitor_nextion, args=(message_queue,))
    monitor_nextion_process.start()

    # Create the poll_senesors_process process
    poll_sensors_process = multiprocessing.Process(target=poll_sensors, args=(message_queue,))
    poll_sensors_process.start()

    # Wait for the monitor_nextion_process to finish
    #monitor_nextion_process.join()

    # Wait for the monitor_nextion_process to finish
    #poll_sensors_process.join()

    print("Processes have finished.")
