#!/usr/bin/env python
"""
Monitoring and controlling Tektronix TDS1012B over USBTMC
Basic driver and example code

Needs Python 2.x at the moment
"""

from __future__ import division
import pylab

DEBUG = True

class Scope:
    """
    Tektronix oscilloscope driver
    Tested with TDS 1012B
    """

    def __init__(self, location=None):
        """ Initialize driver, default location is first usbtmc device """
        if not location:
            location = "/dev/usbtmc0"
        self.handle = open(location, "r+")

    def send(self, cmd):
        """ Send a command to the device """
        if DEBUG:
            print("Send: %s" %(cmd))
        # Terminate with line-feed
        self.handle.write("%s\n" %(cmd))

    def recv(self, timeout=5):
        """ Receive a text response from device """
        self.handle.seek(0, 0)
        return self.handle.readline().strip()

    def query(self, cmd):
        """ Ask and listen for response in one go, for a query command """
        self.send(cmd)
        return self.recv()

    def getdata(self, channel=1):
        """
        Data acquisition from scope

        Input:
        channel: [1/2] which channel to query

        Output:
        Python list of data in -127..+127 range
        """
        size = 2500
        width = 1 # Scope internal data structure uses 8-bit data, here no gain to use width=2
        self.send("DATA:SOURCE CH%d;WIDTH %d;ENCDG RPB;STOP %d" % (channel,width,size))
        self.send("CURVE?")

        # Reply header has the format: #42500?????
        # where "#" is message start,
        # "4" is that 4 ASCII digits will follow
        # "2500" the number of bytes of the data that follows
        # "??????..." binary data, altogether 2500 byte in this case
        tmp = self.handle.read(2)
        digits = int(tmp[1])
        tmp = self.handle.read(digits)
        bytes = int(tmp)
        data = self.handle.read(bytes)

        # On-screen scale -5..+5 division: 1..255
        tonumber = lambda x: ord(x) - 128
        datanum = [tonumber(x) for x in data]
        return datanum



if __name__ == "__main__":
    # Example: data acquisition
    # Some of this might be moved into the Scope class later for convenience

    ####### Settings:
    ####Good values: 1, 2
    channel = 1
    ####

    scope = Scope()
    id = scope.query("*IDN?")
    print("Scope ID string: %s" %(id))
    
    print("Using channel %d" %(channel))

    hscale = float(scope.query("HOR:scale?"))
    vscale = float(scope.query("CH%d:scale?" %(channel)))
    print("X-scale: %g s, Y-scale: %g V" %(hscale, vscale))

    zeropoint = float(scope.query("CH%d:POS?" %(channel)))
    print("Vertical center: %g divisions" %(zeropoint))
    
    # This scaling will be okay for continuous scan and stopped sequence,
    # but wrong if a stopped sequence is vertically shifted by device front knob
    vscaling = lambda x: ((x / 256 * 10) - zeropoint) * vscale
    data = scope.getdata(channel=channel)
    scaleddata = [vscaling(x) for x in data]

    timing = lambda t: t / 2500 * 10 * hscale
    datatime = [timing(t) for t in xrange(2500)]

    pylab.plot(datatime, scaleddata)
    pylab.title("Channel %d" %(channel))
    pylab.xlabel("Time (s)")
    pylab.ylabel("Voltage (V)")
    pylab.show()
