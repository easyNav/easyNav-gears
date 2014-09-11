
import Filters
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
import multiprocessing

# Graph class
class GraphClass:

    # constr
    def __init__(self):
        # plotarr
        maxLen=10
        x = np.linspace(0, maxLen, maxLen)
        y = np.linspace((maxLen/-2), (maxLen/2), maxLen)
        plt.ion()
        self.fig = plt.figure(figsize=(14,7))

        # g1 = self.fig.add_subplot(221, adjustable='box', aspect=0.3)
        # self.g1_line, = g1.plot(x, y, 'r-', label='a')
        # self.g1_line.set_ydata([0,1,2,3,4,5,6,7,8,9])

        self.g2 = self.fig.add_subplot(222, adjustable='box', projection='polar', aspect=0.3)
        self.g2_line, = self.g2.plot(x, y, 'r-', label='a')
        self.g2_line.set_ydata([0])
        self.arrow = self.g2.arrow(-50/180.*np.pi, 0.5, 0, 1, alpha = 1.0, width = 0.055,
                 edgecolor = 'black', facecolor = 'green', lw = 3, zorder = 5)

        # g3 = self.fig.add_subplot(212, adjustable='box', aspect=0.3)
        # self.g3_line, = g3.plot(x, y, 'r-', label='a')
        # self.g3_line.set_ydata([45])

        self.draw()

    # arrow
    def set_angle(self, angle):
        print "Setting angle to: " + str(angle)
        self.arrow.remove()
        self.arrow = self.g2.arrow(angle/180.*np.pi, 0.5, 0, 1, alpha = 1.0, width = 0.055,
                 edgecolor = 'black', facecolor = 'green', lw = 3, zorder = 5)
        self.draw()

    # draw
    def draw(self):
        self.fig.canvas.draw()

    # add data
    def add():
        print "A"

class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    @property
    def value(self):
        return self.val.value

# Serial class
class SerialClass:

    # constr
    def __init__(self, strPort):
        # open serial port
        self.ser = serial.Serial(strPort, 57600)
        self.arr = []
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.mag = 0
        self.gx = 0
        self.gy = 0
        self.gz = 0
        self.ms = 0

    def read(self):
        # read line
        # #YPRMfssT=,-1.24,-2.04,-179.52,1.08,0.04,-0.01,-1.00,10.00,
        line = self.ser.readline()
        self.arr = line.split(",")
        ctrl = self.arr[0]
        if ctrl != "#YPRMfssT=":
            return
        #print line

        self.yaw = float(self.arr[1])
        self.pitch = float(self.arr[2])
        self.roll = float(self.arr[3])
        self.mag = float(self.arr[4])
        self.gx = float(self.arr[5])
        self.gy = float(self.arr[6])
        self.gz = float(self.arr[7])
        self.ms = float(self.arr[8])

    def close(self):
        # close serial
        self.ser.flush()
        self.ser.close()

serial = SerialClass("/dev/tty.usbserial-A600dRYL")

def run_graph(ns):
    graph = GraphClass()
    while(1):
        time.sleep(0.1)
        print ns.mag
        graph.set_angle(ns.yaw)
    #serial.close()


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    ns = manager.Namespace()


    print 'before', ns
    p = multiprocessing.Process(target=run_graph, args=(ns,))
    p.start()

    while(1):
        serial.read()
        ns.yaw=serial.yaw
        ns.mag=serial.mag
        #time.sleep(1)
        #print ns

    p.join()
    print 'after', ns