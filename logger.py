import datetime
import collections
import serial
import string
import sys
import threading
import time


# rotating buffer of data
buffer = collections.deque([], maxlen=10000)

# settings
COM = "/dev/ttyUSB0"
COM = "COM9"

maps = {
    "03": ("Fuel Sys 1 Mode", lambda a, b: a),
#    "04": ("%Load", lambda a: (a / 255) * 100),
    "0C": ("RPM", lambda a, b: (a * 256 + b) / 4),
#    "0D": ("KPH", lambda a: a),
#    "0E": ("Timing advance", lambda a: (a / 2) - 64),
#    "11": ("% Throttle", lambda a: (a * 100) / 255),
#    "49": ("% Accelerator Pedal A", lambda a: (a * 100) / 255),
#    "4A": ("% Accelerator Pedal B", lambda a: (a * 100) / 255),
}

# helper method
def blockdump():
    """ blocks on Enter key, then dumps buffer
    """
    global buffer
    global maps

    raw_input("Press Enter to dump results...")

    dumptime = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S.%f")
    filename = "dump-{0}.txt".format(dumptime)

    with open(filename, "a") as f:

        # write headers
        f.write("Time, ")
        for hex, (units, func) in sorted(maps.items()):
            f.write("{0}, ".format(units))
        f.write("\n")

        # write buffer
        for line in buffer:
            f.write(line + "\n")

        # beep
        print chr(7)

    # restart self
    blockdump()


# set up
ser = serial.Serial(COM, timeout=0.05, baudrate=9600, xonxoff=True)

# reset device
ser.write("ATZ\r")
time.sleep(5)

# set timeout to 40ms
ser.write("ATST 10\r")
time.sleep(1)

# set adaptive timing to aggressive
ser.write("ATAT2\r")
time.sleep(1)

# set up buffer dumper :)
threading.Thread(target=blockdump).start()

# read maps
while True:

    line = "{0}, ".format(datetime.datetime.now().strftime("%H:%M:%S.%f").rstrip('0'))
    for hex, (units, func) in sorted(maps.items()):

        # prepare the outgoing request
        req = "01{0}".format(hex)

        # flush input buffer
        ser.flushInput()

        # send the request
        ser.write("{0}\r".format(req))

        # the data, sans newline and header data
        rl = ""
        while rl == "":
            rl = ser.readline().strip()
        ser.flushInput()

        res = rl.split(" ")[2:-1]

        # parse the result into token, de-hexifier
        tokens = [ord(chr(int(t, 16))) for t in res]
        val = "???"
        try:
            val = func(*tokens)
        except:
            pass
        
        line += "{0}, ".format(val)

    buffer.append(line)
