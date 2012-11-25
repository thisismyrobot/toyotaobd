import serial
import time


COM = "/dev/ttyUSB0"

maps = {"0C": ("RPM", lambda a, b: (a * 256 + b) / 4)}

# set up
ser = serial.Serial(COM, timeout=1)
ser.write("ATZ\r")
time.sleep(4)
print ser.readline()
print ser.readline()
print ser.readline()


# main stuff
while True:
    for hex, (units, func) in maps.items():

        # prepare the outgoing request
        req = "01{0}".format(hex)

        print " > {0}".format(req)

        # send the request
        ser.write("{0}\r".format(req))

        # the data, sans newline and header data, parsed into tokens
        res = ser.readline().strip().split(" ")[2:-1]

        print " < {0}".format(res)

        # parse the result into token, de-hexifier
        tokens = [ord(chr(int(t, 16))) for t in res]
        val = func(*tokens)

        print "{0} {1}".format(val, units)
        time.sleep(0.1)
