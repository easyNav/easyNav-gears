
import Filters
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
import multiprocessing

# Filter
class KalmanFilter(object):

    def __init__(self, process_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def input_latest_noisy_measurement(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

    def get_latest_estimated_measurement(self):
        return self.posteri_estimate

# Smooth
class SmoothClass(object):

    def __init__(self):
        print "SmoothClass"


    def smooth(self, x, window_len=10, window='hanning'):
        """smooth the data using a window with requested size.
        
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        
        input:
            x: the input signal 
            window_len: the dimension of the smoothing window
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.

        output:
            the smoothed signal
            
        example:

        import numpy as np    
        t = np.linspace(-2,2,0.1)
        x = np.sin(t)+np.random.randn(len(t))*0.1
        y = smooth(x)
        
        see also: 
        
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter
     
        TODO: the window parameter could be the window itself if an array instead of a string   
        """
        if x.ndim != 1:
            raise ValueError, "smooth only accepts 1 dimension arrays."

        if x.size < window_len:
            raise ValueError, "Input vector needs to be bigger than window size."

        if window_len < 3:
            return x

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

        s=np.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
        #print(len(s))
        
        if window == 'flat': #moving average
            w = np.ones(window_len,'d')
        else:
            w = getattr(np, window)(window_len)
        y = np.convolve(w/w.sum(), s, mode='same')
        return y[window_len-1:-window_len+1]

    def gauss_kern(self, size, sizey=None):
        """ Returns a normalized 2D gauss kernel array for convolutions """
        size = int(size)
        if not sizey:
            sizey = size
        else:
            sizey = int(sizey)
        x, y = np.mgrid[-size:size+1, -sizey:sizey+1]
        g = np.exp(-(x**2/float(size) + y**2/float(sizey)))
        return g / g.sum()

    def blur_image(self, im, n, ny=None) :
        """ blurs the image by convolving with a gaussian kernel of typical
            size n. The optional keyword argument ny allows for a different
            size in the y direction.
        """
        g = gauss_kern(n, sizey=ny)
        improc = signal.convolve(im, g, mode='valid')
        return(improc)

# Graph class
class GraphClass:

    # constr
    def __init__(self):
        # plotarr
        self.maxLen=200
        x = np.linspace(0, self.maxLen, self.maxLen)
        y = np.linspace(-2.5, 2.5, self.maxLen)
        plt.ion()
        self.fig = plt.figure(figsize=(14,7))

        g1 = self.fig.add_subplot(221, adjustable='box', aspect=10)
        self.g1_line_1, = g1.plot(x, y, 'r-', label='a')
        self.g1_line_2, = g1.plot(x, y, 'g-', label='a')
        self.g1_line_3, = g1.plot(x, y, 'b-', label='a')
        # self.g1_line.set_ydata([0,1,2,3,4,5,6,7,8,9])

        self.g2 = self.fig.add_subplot(222, adjustable='box', projection='polar', aspect=0.3)
        self.g2_line, = self.g2.plot(x, y, 'r-', label='a')
        self.g2_line.set_ydata([0])
        self.arrow = self.g2.arrow(-50/180.*np.pi, 0.5, 0, 1, alpha = 1.0, width = 0.055,
                 edgecolor = 'black', facecolor = 'green', lw = 3, zorder = 5)

        self.g3 = self.fig.add_subplot(212, adjustable='box', aspect=0.3)
        self.g3_line, = self.g3.plot(10, 10, 'r-', label='a', marker='o')
        # self.g3.arrow( 0, 0, 0.0, -0.2, fc="k", ec="k",
        #     head_width=1, head_length=2 )
        self.g3_line.set_ydata([0])
        self.g3_line.set_xdata([0])
        self.g3.set_ylim([-5,5])
        self.g3.set_xlim([-5,5])

        self.draw()

    # arrow
    def set_angle(self, angle):
        #print "Setting angle to: " + str(angle)
        self.arrow.remove()
        self.arrow = self.g2.arrow(angle/180.*np.pi, 0.5, 0, 1, alpha = 1.0, width = 0.055,
                 edgecolor = 'black', facecolor = 'green', lw = 3, zorder = 5)
        self.draw()

    # g3
    def set_g3(self, dist, ang):

        x_arr = self.g3_line.get_xdata()
        y_arr = self.g3_line.get_ydata()
        # dist = dist + y_arr[-1]

        new_xval = dist*np.sin(ang/180.*np.pi)
        new_yval = dist*np.cos(ang/180.*np.pi)

        new_yval = new_yval + y_arr[-1]
        new_xval = new_xval + x_arr[-1]

        print new_xval
        print new_yval
        print "--"

        x_arr.append(new_xval)
        y_arr.append(new_yval)
        print x_arr
        print y_arr
        self.g3_line.set_xdata(x_arr)
        self.g3_line.set_ydata(y_arr)
        self.draw()

    # g1
    def set_g1(self, arr, col):
        f_arr = [];
        for i in xrange(0,self.maxLen):
            f_arr.append(0);

        for m in xrange(0,len(arr)):
            f_arr[m] = arr[m]

        #print f_arr
        if col == "r":
            self.g1_line_1.set_ydata(f_arr)
        elif col == "g":
            self.g1_line_2.set_ydata(f_arr)
        elif col == "b":
            self.g1_line_3.set_ydata(f_arr)
        self.draw()

    # draw
    def draw(self):
        self.fig.canvas.draw()

    # add data
    def add():
        print "A"

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

# Data class
class DataClass:

    # constr
    def __init__(self, raw, kal, smth, ang, vel, dist, ms, total):

        self.raw_arr = raw[:]
        self.kal_arr = kal[:]
        self.smth_arr = smth[:]
        self.ang_arr = ang[:]
        self.vel_arr = vel[:]
        self.dist_arr = dist[:]
        self.ms_arr = ms[:]
        self.total = total

# Crunch class
class CrunchClass:

    # constr
    def __init__(self):
        self.data_arr = []
        self.ms_arr = []
        self.ang_arr = []

        # Hack stab mechanism
        self.stab_count = 0
        self.stop = 0

    def integrate(self, arr, m_arr):
        sum_arr = []
        int_sum = 0
        for i in xrange(0, len(arr)):
            int_sum +=  abs(arr[i] * (m_arr[i]*0.001))
            sum_arr.append(int_sum)
        return sum_arr

    def sumArr(self, arr):
        total = 0
        for i in xrange(0, len(arr)):
            total += arr[i]
        return total

    def add(self, data, ms, ang):

        data-=1

        # Hack stab mechanism
        #if data < 0.07 and data > 0.00:
        if data < 0.16 and data > 0.07:
            self.stab_count += 1
        else:
            self.stab_count -= 1
            self.stop = 0
        if self.stab_count == 5:
            self.stop = 1
            self.stab_count = 0

        # Add data if moving
        if self.stop == 0:
            self.data_arr.append(data)
            self.ms_arr.append(ms)
            self.ang_arr.append(ang)

        # Collect list if stopped
        if self.stop == 1:

            r_arr = self.data_arr[:]
            m_arr = self.ms_arr[:]
            a_arr = self.ang_arr[:]

            self.data_arr = []
            self.ms_arr = []
            self.ang_arr = []

            if len(r_arr) > 10:

                """
                KalmanFilter
                """
                measurement_standard_deviation = np.std(r_arr)
                process_variance = 1e-3
                estimated_measurement_variance = measurement_standard_deviation ** 2
                kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
                posteri_estimate_graph = []
                for iteration in xrange(0, len(r_arr)):
                    kalman_filter.input_latest_noisy_measurement(r_arr[iteration])
                    posteri_estimate_graph.append(kalman_filter.get_latest_estimated_measurement())

                """
                Smoothing
                """
                Smoother = SmoothClass()
                smoothed_arr = Smoother.smooth( np.array(r_arr) ,10,'blackman')

                """
                Integral
                """
                vel_smoothed_arr = self.integrate(smoothed_arr, m_arr)
                dist_smoothed_arr = self.integrate(vel_smoothed_arr, m_arr)

                vel_kal_arr = self.integrate(posteri_estimate_graph, m_arr)
                dist_kal_arr = self.integrate(vel_kal_arr, m_arr)

                total_smoothed = self.sumArr(dist_smoothed_arr)
                total_kal = self.sumArr(dist_kal_arr)


                print "--"
                print a_arr[0]
                print a_arr[-1]
                print total_smoothed
                print total_kal
                print (total_smoothed+total_kal)/2
                print "--"


                """
                Dataset
                """
                return DataClass(raw=r_arr, kal=posteri_estimate_graph, smth=smoothed_arr, ang=a_arr, vel=vel_smoothed_arr, dist=dist_smoothed_arr, ms=m_arr, total=(total_smoothed+total_kal)/2)

            else:
                return None
        else:
            return None
            
        #print data

        # if data > 1.1:
        #     self.data_arr.append(data)
        #     self.ms_arr.append(ms)
        #     self.ang_arr.append(ang)
        #     print data

        #     self.cap = 1

        #if self.cap

def run_graph(ns):
    graph = GraphClass()
    # graph.set_g3(3,30)
    # graph.set_g3(1,0)
    # graph.set_g3(1,-30)
    # graph.set_g3(1,-90)
    # graph.set_g3(1,-130)
    # graph.set_g3(1,-180)

    while(1):
        time.sleep(0.1)
        graph.set_angle(ns.yaw)
        if ns.ping == 1:
            ns.ping = 0;
            graph.set_g3(ns.total,ns.yaw)
            graph.set_g1(ns.raw_arr, "r")
            graph.set_g1(ns.smth_arr, "g")
            graph.set_g1(ns.vel_arr, "b")

    serial.close()

"""
Algorithm

1. On Footrelease/Non zero, catch accel data stream
    until Footpress/Zero
    catch initial angle, and final angle
2. Once we got the dataset, process it immediately
    1. Clean data
    2. Double integrate
    3. Account for prev angle and final angle. do trigo
    4. Pass datasets to graph
"""

if __name__ == '__main__':

    # Classes
    serial = SerialClass("/dev/tty.usbserial-A600dRYL")
    crunch = CrunchClass()

    # Mp Manager
    manager = multiprocessing.Manager()
    ns = manager.Namespace()

    # Data
    ns.raw_arr = []
    ns.kal_arr = []
    ns.smth_arr = []
    ns.vel_arr = []
    ns.dist_arr = []
    ns.ang_arr = []
    ns.ms_arr = []
    ns.yaw = 0
    ns.total = 0
    ns.ping = 0

    # Mp
    p = multiprocessing.Process(target=run_graph, args=(ns,))
    p.start()

    # Serial Loop
    while(1):
        serial.read()
        ns.yaw=serial.yaw

        data_obj = crunch.add(serial.mag, serial.ms, serial.yaw)
        if data_obj != None:
            ns.raw_arr = data_obj.raw_arr
            ns.kal_arr = data_obj.kal_arr
            ns.smth_arr = data_obj.smth_arr
            ns.vel_arr = data_obj.vel_arr
            ns.dist_arr = data_obj.dist_arr
            ns.ang_arr = data_obj.ang_arr
            ns.ms_arr = data_obj.ms_arr
            ns.total = data_obj.total
            ns.ping = 1

    p.join()
    print 'after', ns