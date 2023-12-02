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


def monitor_nextion(queue, messages):
    while True:
        command = nextion.monitor_nextion()

        if command:
            print("From the process:", command[0])
            queue.put(command)
        else:
            print("Command is empty")

        time.sleep(2)

def poll_sensors(queue):
    loop_poll_sensors = False
    while True:
        command = queue.get()

        # Check if message is cmd1, set loop_poll_sensors to True
        if command:
            if command[0] == "cmd1":
                loop_poll_sensors = True
                while loop_poll_sensors:
                    ezo.poll_sensors(poll_sensor_list, triggers_actions)

                    cmd = queue.get()

                    if cmd[0] == "cmd2":
                        loop_poll_sensors = False


if __name__ == "__main__":
    # Create a multiprocessing Queue
    message_queue = multiprocessing.Queue()

    # Define a list of messages to be sent
    messages_to_send = []

    # Create the monitor_nextion_process process
    monitor_nextion_process = multiprocessing.Process(target=monitor_nextion, args=(message_queue, messages_to_send))
    monitor_nextion_process.start()

    # Create the poll_senesors_process process
    poll_sensors_process = multiprocessing.Process(target=poll_sensors, args=(message_queue,))
    poll_sensors_process.start()

    # Wait for the monitor_nextion_process to finish
    monitor_nextion_process.join()

    # Wait for the monitor_nextion_process to finish
    poll_sensors_process.join()

    print("Processes have finished.")
