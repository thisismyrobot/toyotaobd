import serial
import sys
import time


COM = "/dev/ttyUSB0"

maps = {
    "0C": ("RPM", lambda a, b: (a * 256 + b) / 4),
    "0D": ("KPH", lambda a: a)
       }

# set up
ser = serial.Serial(COM, timeout=1)

# reset device
ser.write("ATZ\r")
time.sleep(5)
ser.readline()

# set timeout to 40ms
ser.write("ATST 10\r")
time.sleep(1)
ser.readline()

# set adaptive timing to aggressive
ser.write("ATAT2\r")
time.sleep(1)
ser.readline()

# read maps
while True:

    sys.stdout.write("{0}, ".format(time.time()))

    for hex, (units, func) in maps.items():

        # prepare the outgoing request
        req = "01{0}".format(hex)

        # send the request
        ser.write("{0}\r".format(req))

        # the data, sans newline and header data, parsed into tokens
        res = ser.readline().strip().split(" ")[2:-1]

        # parse the result into token, de-hexifier
        tokens = [ord(chr(int(t, 16))) for t in res]
        val = func(*tokens)

        sys.stdout.write("{0} {1},".format(val, units))

    sys.stdout.write("\n")
