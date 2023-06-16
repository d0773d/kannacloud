import asyncio
import board
import busio
import time
import serial

from multiprocessing import Process
from ezo_sensors import Ezo

ser = serial.Serial('/dev/ttyAMA1', 9600, timeout=1)

# instantiate the objects
res = Ezo(0x66, "tmp", False)
humidity = Ezo(0x6F, "hum", False)
ph = Ezo(0x63, "ph", False)

def monitor_nextion():
    while True:
        data = ser.readline()
        print(data)

        if data is not None:
            # convert bytearray to string
            data_string = ''.join([chr(b) for b in data])

            substrings = []
            in_brackets = False
            current_substring = ""
            for c in data_string:
                if c == "<":
                    in_brackets = True
                elif c == ">" and in_brackets:
                    substrings.append(current_substring)
                    current_substring = ""
                    in_brackets = False
                elif in_brackets:
                    current_substring += c
            if current_substring:
                substrings.append(current_substring)
            # using set()
            # to remove duplicate commands
            # from list
            substrings = list(set(substrings))

            print("The command between <> : " + str(substrings))

def get_res_temp():
    while True:
        print("res")
        res.cmd_r()

def get_hum():
    while True:
        humidity.cmd_r()

def get_ph():
    while True:
        ph.cmd_r()

# Create a new process with a specified function to execute.
uart_monitor = Process(target=monitor_nextion)
res_temp_val = Process(target=get_res_temp)
hum_val = Process(target=get_hum)
ph_val = Process(target=get_ph)

# Run the new process
uart_monitor.start()
res_temp_val.start()
hum_val.start()
ph_val.start()
