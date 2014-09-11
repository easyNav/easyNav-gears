import matplotlib
import numpy as np
import matplotlib.pyplot as plt

print "matplotlib.__version__   = ", matplotlib.__version__
print "matplotlib.get_backend() = ", matplotlib.get_backend()


# radar green, solid grid lines
plt.rc('grid', color='#316931', linewidth=1, linestyle='-')
plt.rc('xtick', labelsize=15)
plt.rc('ytick', labelsize=15)

# force square figure and square axes looks better for polar, IMO
width, height = matplotlib.rcParams['figure.figsize']
size = min(width, height)
# make a square figure
fig = plt.figure(figsize=(size, size))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True, axisbg='#d5de9c')

r = np.arange(0, 3.0, 0.01)
theta = 2*np.pi*r
ax.plot(theta, r, color='#ee8d18', lw=3)
ax.set_rmax(2.0)
plt.grid(True)

ax.set_title("And there was much rejoicing!", fontsize=20)
#This is the line I added:
# arr1 = plt.arrow(0, 0.5, 0, 1, alpha = 0.5, width = 0.015,
#                  edgecolor = 'black', facecolor = 'green', lw = 2, zorder = 5)

# # arrow at 45 degree
# arr2 = plt.arrow(45/180.*np.pi, 0.5, 0, 1, alpha = 0.5, width = 0.015,
#                  edgecolor = 'black', facecolor = 'green', lw = 2, zorder = 5)

plt.show()