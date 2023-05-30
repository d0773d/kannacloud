import asyncio
import board
import busio
import time

from ezo_sensors import Ezo

uart = busio.UART(board.TX, board.RX, baudrate=9600)

# instantiate the objects
res = Ezo(0x66, "tmp", False)
humidity = Ezo(0x6F, "hum", False)
ph = Ezo(0x63, "ph", False)

async def get_res_temp():
    while True:
        res.cmd_r()

        # allow other tasks to do work
        await asyncio.sleep(0)

async def get_hum():
    while True:
        humidity.cmd_r()

        # allow other tasks to do work
        await asyncio.sleep(0)

async def get_ph():
    while True:
        ph.cmd_r()

        # allow other tasks to do work
        await asyncio.sleep(0)

async def monitor_uart():
    while True:
        data = uart.read(32)  # read up to 32 bytes

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
            
            print("The element between <> : " + str(substrings))

        # allow other tasks to do work
        await asyncio.sleep(0)

# main coroutine
async def main():  # Don't forget the async!
    # create uart task
    uart_task = asyncio.create_task(
        monitor_uart()
    )

    # create sensor tasks
    res_temp_task = asyncio.create_task(
        get_res_temp()
    )
    hum_task = asyncio.create_task(
        get_hum()
    )
    ph_task = asyncio.create_task(
        get_ph()
    )

    # start all of the tasks
    await asyncio.gather(
        uart_task, res_temp_task, hum_task, ph_task
    )  # Don't forget the await!

# start the main coroutine
asyncio.run(main())
