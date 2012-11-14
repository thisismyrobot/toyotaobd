import serial
import time


COM = "COM9"

maps = {"0C": ("RPM", lambda a, b: (a * 256 + b) / 4)}

# main stuff
ser = serial.Serial(COM, timeout=1)
for hex, (units, func) in maps:

    # prepare the outgoing request
    req = "01{0}".format(hex)

    print " > {0}" + req

    # send the request
    ser.write("{0}\n".format(req));
    ser.readline() # the echo of sent data

    # the data, sans newline and header data
    res = ser.readline().trim().split(" ")[2:]

    print " < {0}" + res

    # parse the result into token, de-hexifier
    tokens = [ord(t) for t in res.split(" ")]
    val = func(*tokens)

    print " = {0} {1}".format(val, units)
    time.sleep(1000)