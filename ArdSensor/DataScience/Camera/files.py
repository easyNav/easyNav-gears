import numpy as np
import cv2
import time
import cv
from pytesseract import image_to_string
from PIL import Image
import math



##################################
#			TRACKBAR			 #
##################################

var1 = 0
var2 = 0
var3 = 0

def nothing(x):
	print x
	pass

enable = 1
test = 0

if test:
	img = cv2.imread('image.jpg')
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	height, width, depth = img.shape

	# Create a black image, a window
	cv2.namedWindow('image')

	# create trackbars for color change
	cv2.createTrackbar('var1','image',63,255,nothing)
	cv2.createTrackbar('var2','image',150,255,nothing)
	cv2.createTrackbar('var3','image',3,255,nothing)

##################################
#				LINE			 #
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

	def line_intersection(self,line):

		x1 = self.x1
		y1 = self.y1
		x2 = self.x2
		y2 = self.y2
		x3 = line.x1
		y3 = line.y1
		x4 = line.x2
		y4 = line.y2

		d = ((x1-x2) * (y3-y4)) - ((y1-y2) * (x3-x4))
		if d != 0:
			x_point = ((x1*y2 - y1*x2) * (x3-x4) - (x1-x2) * (x3*y4 - y3*x4)) / d;
			y_point = ((x1*y2 - y1*x2) * (y3-y4) - (y1-y2) * (x3*y4 - y3*x4)) / d;
			return x_point,y_point
		return None

def distance_between_points(p1,p2):
	x1 = p1[0]
	x2 = p2[0]
	y1 = p1[1]
	y2 = p2[1]
	return math.hypot(x2 - x1, y2 - y1)

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

def get_points(line_arr, raw=0, binned_x=0, binned_y=0, variance=1):
	# Intersections
	point_dict = dict()
	point_x_arr = []
	point_y_arr = []
	point_arr = []
	for i, line1 in enumerate(line_arr):
		for m, line2 in enumerate(line_arr):
			point = line1.line_intersection(line2)
			if point != None:
				point_dict[str(point[0])] = point[1]
				point_x_arr.append(point[0])
				point_y_arr.append(point[1])
				point_arr.append([point[0],point[1]])

	if raw:
		return point_arr

	point_x_bin = bin_array(point_x_arr,variance,1)
	point_y_bin = bin_array(point_y_arr,variance,0)

	if binned_x:
		point_arr = []
		for x_key in point_x_bin.keys():
			x = int(point_x_bin[x_key])
			y = int(point_dict[str(x)])

			if binned_y:
				# Averaging the angle also
				for y_key in point_y_bin.keys():
					y_arr = point_y_bin[y_key]
					floaty = float(y)
					if floaty in y_arr:
						y = int(sum(y_arr)/len(y_arr))
						break

			if x>0 and y>0:
				point_arr.append([x,y])

		return point_arr

def get_corners(point_arr):

	# Center point
	center=[0,0];
	for point in point_arr:
		center[0] += point[0];
		center[1] += point[1];

	center[0] *= (1. / len(point_arr))
	center[1] *= (1. / len(point_arr))

	top = []
	bot = []
	for point in point_arr:
		if point[1] < center[1]:
			top.append(point)
		else:
			bot.append(point)

	tl = top[1] if (top[0][0] > top[1][0]) else top[0]
	tr = top[0] if (top[0][0] > top[1][0]) else top[1]
	bl = bot[1] if (bot[0][0] > bot[1][0]) else bot[0]
	br = bot[0] if (bot[0][0] > bot[1][0]) else bot[1]

	return { "tl":tl, "tr":tr, "bl":bl, "br":br, "center":center }

def get_text(frame):
	arr = np.array(frame)
	img = Image.fromarray(arr)
	print(image_to_string(img))

if test:
	while(1):

		# Variables to play
		var1 = cv2.getTrackbarPos('var1','image')
		var2 = cv2.getTrackbarPos('var2','image')
		var3 = cv2.getTrackbarPos('var3','image')

		# Enable
		if not enable:
			k = cv2.waitKey(1) & 0xFF
			if k == 27:
				break
			continue

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

		# Get points
		point_arr = get_points(line_arr)
		for point in point_arr:
			cv2.circle(lined_gray,(point[0],point[1]),5,(0,255,0),2)

		# Check if at least 4 points
		if len(point_arr) < 3:
			print "TOO FEW POINTS"
			cv2.imshow('image',lined_gray)
			k = cv2.waitKey(1) & 0xFF
			if k == 27:
				break
			continue

		# Contour test
		# print "--"
		# contours,h = cv2.findContours(edges,1,2)
		# for cnt in contours:
		# 	approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
		# 	cv2.drawContours(lined_gray,[cnt],0,255,-1)
			# for point in approx:
			# 	point = point[0]
			# 	cv2.circle(lined_gray,(point[0],point[1]),5,(0,255,0),2)

		# Check if exactly 4 points
		if len(point_arr) > 4:
			print "TOO MANY POINTS"
			cv2.imshow('image',lined_gray)
			k = cv2.waitKey(1) & 0xFF
			if k == 27:
				break
			continue

		# Get corners
		corner_dict = get_corners(point_arr)
		cv2.circle(lined_gray,(int(corner_dict["center"][0]),int(corner_dict["center"][1])),5,(0,255,0),2)

		# Stretch
		stretch_height = height + 100

		src = np.array([corner_dict["tl"],corner_dict["tr"],corner_dict["bl"],corner_dict["br"]],np.float32)
		dst = np.array([[0,0],[width,0],[0,stretch_height],[width,stretch_height]],np.float32)

		M = cv2.getPerspectiveTransform(src,dst)
		dst = cv2.warpPerspective(img,M,(width,stretch_height))

		# Text
		#edges = cv2.Canny(dst,255,200,3)
		#get_text(dst)

		# Display image
		cv2.imshow('image',dst)
		k = cv2.waitKey(1) & 0xFF
		if k == 27:
			break


cv2.destroyAllWindows()