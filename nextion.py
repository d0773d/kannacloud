import asyncio
import board
import busio
import time
import serial

ser = serial.Serial('/dev/ttyAMA1', 9600, timeout=1)

class Nextion:
    def __init__(self):
        print("Loading Nextion")

    def monitor_nextion(self):
        data = ser.readline()

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
