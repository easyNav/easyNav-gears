
 
import sys, serial, argparse
import numpy as np
from time import sleep
from collections import deque

import time
import threading
 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation


"""
Written by RAAJ
"""

# plot class
class AnalogPlot:

  # constr
  def __init__(self, strPort, maxLen):
    # open serial port
    self.ser = serial.Serial(strPort, 57600)
 
    self.ax = deque([0.0]*maxLen)
    self.ay = deque([0.0]*maxLen)
    self.maxLen = maxLen

    x = np.linspace(0, maxLen, maxLen)
    y = np.linspace((maxLen/-2), (maxLen/2), maxLen)
    plt.ion()
    self.fig = plt.figure(figsize=(10,4))
    ax = self.fig.add_subplot(1,1,1, adjustable='box', aspect=0.3)
    self.line1, = ax.plot(x, y, 'r-')

  def update(self):
    line = self.ser.readline()
    data_arr = line.split("~")
    xval = float(data_arr[1])
    ts = float(data_arr[3].rstrip('\n'))
    data=[ts,xval]
    print data
    self.add(data)
    self.line1.set_ydata(self.ay)
    #self.line1.set_xdata(self.ax)
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
    assert(len(data) == 2)
    self.addToBuf(self.ax, data[0])
    self.addToBuf(self.ay, data[1])

  # clean up
  def close(self):
    # close serial
    self.ser.flush()
    self.ser.close()  

# main() function
def main():
  # create parser
  parser = argparse.ArgumentParser(description="LDR serial")
  parser.add_argument('--port', dest='port', required=True) 
  args = parser.parse_args()  
  strPort = args.port


  analogPlot = AnalogPlot(strPort, 300)
  while(1):
    print "X"
    analogPlot.update()

  analogPlot.close()
  print('exiting.')
  
 
# call main
if __name__ == '__main__':
  main()