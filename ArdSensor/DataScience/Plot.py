
 
import sys, serial, argparse
import numpy as np
from time import sleep
from collections import deque

import time
import threading
 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation


import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
"""
Written by RAAJ
"""

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

# plot class
class AnalogPlot:

  # constr
  def __init__(self, strPort, maxLen):

    # open serial port
    self.Smoother = SmoothClass()
    self.ser = serial.Serial(strPort, 57600)

    # indexes
    self.accelx_index = 1
    self.accely_index = 2
    self.accelz_index = 3
    self.gyrox_index = 4
    self.gyroy_index = 5
    self.gyroz_index = 6
    self.compassx_index = 7
    self.compassy_index = 8
    self.compassz_index = 9

    # dataarr
    self.plot1_arr = deque([0.0]*maxLen)
    self.plot2_arr = deque([0.0]*maxLen)
    self.plot3_arr = deque([0.0]*maxLen)
    self.maxLen = maxLen

    self.stableCount = 0
    self.collect = 0
    self.arrFirst = 0

    # plotarr
    x = np.linspace(0, maxLen, maxLen)
    y = np.linspace((maxLen/-2), (maxLen/2), maxLen)
    plt.ion()
    self.fig = plt.figure(figsize=(14,7))
    ax = self.fig.add_subplot(1,1,1, adjustable='box', aspect=0.3)
    self.plot1_line, = ax.plot(x, y, 'r-', label='a')
    self.plot2_line, = ax.plot(x, y, 'g-', label='b')
    self.plot3_line, = ax.plot(x, y, 'b-', label='c')

  def integrate(self, arr):
    sum_arr = []
    int_sum = 0
    for i in xrange(0, self.maxLen):
        int_sum +=  arr[i] * 0.04
        sum_arr.append(int_sum)
    return sum_arr

  def clearArr(self, arr):
    for i in xrange(0, self.maxLen):
        arr[i] =  0

  def sumArr(self, arr):
    total = 0
    for i in xrange(0, self.maxLen):
        total += arr[i]
    return total

  def update(self):

    # (Read data)
    line = self.ser.readline()
    data_arr = line.split("~")

    ## (AccelX)
    accelx = float(data_arr[self.accelx_index])-20
    if (accelx < 10) and (accelx > -10):
        accelx = 0
    else:
        #accelx = accelx/27.5
        print

    ## (AccelY)
    accely = float(data_arr[self.accely_index])-5
    if (accely < 10) and (accely > -10):
        accely = 0
    else:
        accely = accely/27.5
        print

    ## (Sim of stop no count)
    if accelx==0 and accely==0:
        # collect 100 units of blanks, then stop
        if self.stableCount == 10:
            self.arrFirst = 0
            return
        self.stableCount+=1
    else:
        # Need to clear array on first run
        if self.arrFirst == 0:
            self.arrFirst = 1
            self.clearArr(self.plot1_arr)
        self.stableCount = 0

    ## (Other points)
    accelz = float(data_arr[self.accelz_index])-15
    gyrox = float(data_arr[self.gyrox_index])/500 + 105
    gyroy = float(data_arr[self.gyroy_index])/500 + 105
    gyroz = float(data_arr[self.gyroz_index])/500 + 105
    compassx = float(data_arr[self.compassx_index])/10000
    compassy = float(data_arr[self.compassy_index])/10000
    compassz = float(data_arr[self.compassz_index])/10000

    ## (Add points)
    data = [0, accelx, accely, accelz, gyrox, gyroy, gyroz, compassx, compassy, compassz]
    plot_data = [accelx, accely, compassx]
    self.add(plot_data)
    print plot_data

    ## (Kalman filter)
    # measurement_standard_deviation = np.std(self.plot1_arr)
    # process_variance = 1e-3
    # estimated_measurement_variance = measurement_standard_deviation ** 2  # 0.05 ** 2
    # kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
    # posteri_estimate_graph = []
    # for iteration in xrange(0, self.maxLen):
    #     kalman_filter.input_latest_noisy_measurement(self.plot1_arr[iteration])
    #     posteri_estimate_graph.append(kalman_filter.get_latest_estimated_measurement())

    ## (Smoothing and integration)
    from scipy import integrate
    smooth_accelx_arr = self.Smoother.smooth( np.array(self.plot1_arr) ,10,'blackman')
    velx_plot = self.integrate(smooth_accelx_arr)
    distx_plot = self.integrate(velx_plot)

    print self.sumArr(distx_plot)


    # velx_plot = []
    # velc_sum = 0
    # for i in xrange(0, self.maxLen):
    #     velc_sum +=  smooth_accelx_arr[i] * 0.04
    #     velx_plot.append(velc_sum)
    # distx_plot = []
    # dist_sum = 0
    # for i in xrange(0, self.maxLen):
    #     dist_sum +=  velx_plot[i] * 0.04
    #     distx_plot.append(dist_sum)


    ## Plot
    # self.plot1_line.set_ydata(self.plot1_arr)
    # self.plot2_line.set_ydata(smooth_accelx_arr)

    self.plot1_line.set_ydata(smooth_accelx_arr)
    self.plot2_line.set_ydata(velx_plot)
    self.plot3_line.set_ydata(distx_plot)
    self.fig.canvas.draw()

  # add to buffer
  def addToBuf(self, buf, val):
    if len(buf) < self.maxLen:
      buf.append(val)
    else:
      buf.pop()
      buf.appendleft(val)
 
  # add data
  def add(self, data):
    assert(len(data) == 3)
    self.addToBuf(self.plot1_arr, data[0])
    self.addToBuf(self.plot2_arr, data[1])
    self.addToBuf(self.plot3_arr, data[2])

  # clean up
  def close(self):
    # close serial
    self.ser.flush()
    self.ser.close()  

# main() function
def main():
  # create parser
  # parser = argparse.ArgumentParser(description="LDR serial")
  # parser.add_argument('--port', dest='port', required=True) 
  # args = parser.parse_args()  
  # strPort = args.port

  strPort = "/dev/tty.usbserial-A600dRYL"

  analogPlot = AnalogPlot(strPort, 100)
  while(1):
    #print "X"
    analogPlot.update()

  analogPlot.close()
  print('exiting.')
  
 
# call main
if __name__ == '__main__':
  main()