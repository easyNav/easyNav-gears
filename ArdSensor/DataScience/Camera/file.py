import numpy as np
import cv2
import time
import cv


img = cv2.imread('image.jpg',1)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

##################################
#			TRACKBAR             #
##################################

var1 = 0
var2 = 0
var3 = 0

def nothing(x):
	print x
	pass

# Create a black image, a window
cv2.namedWindow('image')

# create trackbars for color change
cv2.createTrackbar('var1','image',63,255,nothing)
cv2.createTrackbar('var2','image',150,255,nothing)
cv2.createTrackbar('var3','image',3,255,nothing)

##################################
#				LINE             #
##################################

class Line(object):

	def __init__(self, rho, theta):
		a = np.cos(theta)
		b = np.sin(theta)
		x0 = a*rho
		y0 = b*rho
		extend = 1000
		x1 = int(x0 + extend*(-b))
		y1 = int(y0 + extend*(a))
		x2 = int(x0 - extend*(-b))
		y2 = int(y0 - extend*(a))

		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2

def bin_array(arr, variance, avg_mode):
	#arr = [95,96,97,201,202]

	arr.sort()

	arr_binned = dict()
	i = 0
	m = 0
	while(1):
		if len(arr) != i+m:  
			curr = arr[i]
			next = arr[i+m]
			if abs(curr-next) < variance:

				if str(curr) in arr_binned:
					arr_binned[str(curr)].append(next)
				else:
					arr_binned[str(curr)]=[curr]
				m+=1
			else:
				i=i+m
				m=0
		else:
			break

	for key in arr_binned.keys():
		num_arr = arr_binned[key]
		avg = sum(num_arr)/len(num_arr)
		#arr_binned[key] = round(avg,1)
		if avg_mode == 1:
			arr_binned[key] = round(float(key),1)

	return arr_binned

#define DEG2RADs(x) ((PI / 180.0) * x)
#define RAD2DEGs(x) ((180.0 / PI) * x)

def rad2deg(rad):
	return 180 * (rad / np.pi)

def deg2rad(deg):
	return ((np.pi / 180.0) * deg)

def get_lines(lines):
	# Get the row and theta values into data strucutes
	rho_arr=[]
	theta_arr=[]
	rho_theta_dict = dict()
	for rho,theta in lines[0]:
		theta_degree = round(rad2deg(theta),1)
		rho_arr.append(rho)
		theta_arr.append(theta_degree)
		rho_theta_dict[str(rho)]=str(theta_degree)

	# Bin them
	line_arr = []
	rho_bin = bin_array(rho_arr,15,1)
	#theta_bin = bin_array(theta_arr,10,0)

	# Iterate and get values
	for rho_key in rho_bin.keys():
		rho = rho_bin[rho_key]
		theta_deg = float(rho_theta_dict[rho_key])

		# Averaging the angle also
		# for theta_key in theta_bin.keys():
		# 	theta_arr = theta_bin[theta_key]
		# 	print theta_arr
		# 	if theta_deg in theta_arr:
		# 		theta_deg = sum(theta_arr)/len(theta_arr)
		# 		break

		theta = deg2rad(theta_deg)

		line = Line(rho, theta)
		line_arr.append(line)

	return line_arr

while(1):

	# Variables to play
	var1 = cv2.getTrackbarPos('var1','image')
	var2 = cv2.getTrackbarPos('var2','image')
	var3 = cv2.getTrackbarPos('var3','image')

	# First get edges through canny
	edges = cv2.Canny(gray,255,200,3)

	# Get hough lines
	lined_gray = np.copy(gray)
	lines = cv2.HoughLines(edges,1,np.pi/180,var1,var2) #minLineLength,maxLineGap
	if lines == None:
		continue

	# Iterate and get values
	line_arr = get_lines(lines)
	for line in line_arr:
		cv2.line(lined_gray,(line.x1,line.y1),(line.x2,line.y2),(0,0,255),2)
	
	# for rho,theta in lines[0]:

	# 	# #print rho
	# 	# if len(lines[0])-1 != i:  
	# 	# 	curr = lines[0][i][0]
	# 	# 	next = lines[0][i+1][0]
	# 	# 	if abs(curr-next) < 10:
	# 	# 		print curr

	# 	#print i
	# 	#print rad2deg(theta)
	# 	a = np.cos(theta)
	# 	b = np.sin(theta)
	# 	x0 = a*rho
	# 	y0 = b*rho
	# 	extend = 1000
	# 	x1 = int(x0 + extend*(-b))
	# 	y1 = int(y0 + extend*(a))
	# 	x2 = int(x0 - extend*(-b))
	# 	y2 = int(y0 - extend*(a))

	# 	cv2.line(lined_gray,(x1,y1),(x2,y2),(0,0,255),2)
	# print "--"

	# Display image
	cv2.imshow('image',lined_gray)
	k = cv2.waitKey(1) & 0xFF
	if k == 27:
		break


cv2.destroyAllWindows()