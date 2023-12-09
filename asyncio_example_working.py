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
ezo = Ezo()
init = Initialize(ezo) # Pass the ezo object to the Initialize class to set the sensor i2c addresses to be used in sensor commands
nextion = Nextion()

sensor_list = ezo.get_sensor_types_addresses()
sensors_triggers_actions = ezo.get_triggers_and_actions()

async def poll_sensors():
    # This code checks to see if the RTD is in front of the list.  If it isn't, then move it to the front of the list
    # This way the script can run faster and not have to wait for a poll cycle to skip the temp compensated sensors
    # The poll cycle will now beable to start at the RTD then continue to the rest of the sensors.

    # Check if 'RTD' is in the list and not already at the front
    if any(sensor['type'] == 'RTD' for sensor in sensor_list) and sensor_list[0]['type'] != 'RTD':
        # Find the index of the dictionary with 'type' equal to 'RTD'
        rtd_index = next((index for index, sensor in enumerate(sensor_list) if sensor['type'] == 'RTD'), None)
        
        if rtd_index is not None:
            # Move the dictionary with 'type' equal to 'RTD' to the front
            sensor_list.insert(0, sensor_list.pop(rtd_index))

    while True:
        print("Polling sensors...")
        await asyncio.sleep(1)
        for device in sensor_list:
            await asyncio.sleep(1)

            #ezo.cmd_r(device["type"], device["address"], triggers_actions)
            ezo.send_sensor_cmd(device["address"], sensor_type=device["type"], cal_mode=False, triggers_actions=sensors_triggers_actions)

            await asyncio.sleep(1)

        await asyncio.sleep(1)

async def sensor_calibrate(command_queue):
    while True:
        print("Calibrating sensors...")
        ezo.send_sensor_cmd(ezo.ezo_sensor_settings["ph_i2c_addr"], sensor_type="pH", cal_mode=True)
        #ezo.send_sensor_cmd(ezo.ezo_sensor_settings["ph_i2c_addr"], "Cal,mid,7.00", cal_mode=True)
        print("Sensor calibration complete.")
        await asyncio.sleep(3)

async def other_function1():
    print("Executing other function 1...")
    # Simulate other function 1
    await asyncio.sleep(2)
    print("Other function 1 complete.")

async def other_function2():
    print("Executing other function 2...")
    # Simulate other function 2
    await asyncio.sleep(2)
    print("Other function 2 complete.")

async def monitor_nextion(command_queue):
    poll_sensors_task = None
    calibrate_sensor_task = None

    poll_sensors_task = asyncio.create_task(poll_sensors())

    while True:
        uart_data = nextion.monitor_nextion()
        if len(uart_data) != 0:
            await command_queue.put(uart_data[0])

            if uart_data[0] == "cmd1":
                if calibrate_sensor_task is not None and not calibrate_sensor_task.done():
                    print("Received cmd1. Stopping calibrate_sensor_task...")
                    calibrate_sensor_task.cancel()

                if poll_sensors_task is None or poll_sensors_task.done():
                    print("Starting poll_sensors...")
                    poll_sensors_task = asyncio.create_task(poll_sensors())
            elif uart_data[0] == "cmd2":
                if poll_sensors_task is not None and not poll_sensors_task.done():
                    print("Received cmd2. Stopping poll_sensors_task...")

                    poll_sensors_task.cancel()
                    calibrate_sensor_task = asyncio.create_task(sensor_calibrate(command_queue))
            elif uart_data[0] == "cmd3":
                print("Received cmd3. Starting other_function1...")
                await other_function1()
            elif uart_data[0] == "cmd4":
                print("Received cmd4. Starting other_function2...")
                await other_function2()
            elif uart_data[0] == "cmd5":
                print("Received cmd5. Canceling sensor_calibrate...")
                calibrate_sensor_task.cancel()
            elif uart_data[0] == "exit":
                if poll_sensors_task is not None and not poll_sensors_task.done():
                    print("Stopping poll_sensors before exiting...")
                    poll_sensors_task.cancel()
                    try:
                        await poll_sensors_task
                    except asyncio.CancelledError:
                        pass
                print("Exiting...")
                break
            else:
                print(f"Invalid command from UART: {uart_data}")

        await asyncio.sleep(1)

if __name__ == "__main__":
    command_queue = asyncio.Queue()

    asyncio.run(monitor_nextion(command_queue))
