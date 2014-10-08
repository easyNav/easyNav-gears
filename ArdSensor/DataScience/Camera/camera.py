import numpy as np
import cv2
import cv2.cv as cv
import time
from pytesseract import image_to_string
from PIL import Image


cap = cv2.VideoCapture(0)
cap.set(3,800)
cap.set(4,600)
# fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
# video_writer = cv2.VideoWriter("output.avi", fourcc, 25, (640, 480))
#video_writer = cv2.VideoWriter("output.mp4",cv2.cv.CV_FOURCC('F','M','P', '4'), 15, (640, 480), 1)

def get_text(frame):
	arr = np.array(frame)
	img = Image.fromarray(arr)
	print(image_to_string(img))

def detect_circles(gray):
	#1, src_gray2.rows/8, 200, 20, 0, 0
	circles = cv2.HoughCircles(gray,cv.CV_HOUGH_GRADIENT, 0.5,10,param1=200,param2=50,minRadius=0,maxRadius=50)
	#circles = cv2.HoughCircles(gray,cv.CV_HOUGH_GRADIENT, 0.5,10)
	if circles == None:
		#print "NONE"
		return

	print circles
	#circles = cv2.HoughCircles(frame,cv.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=0,maxRadius=0)
	circles = np.uint16(np.around(circles))

	for i in circles[0,:]:
		# draw the outer circle
		cv2.circle(gray,(i[0],i[1]),i[2],(0,255,0),2)
		# draw the center of the circle
		cv2.circle(gray,(i[0],i[1]),2,(0,255,0),3)

def draw_corners(gray,frame):
	gray = np.float32(gray)
	dst = cv2.cornerHarris(gray,2,3,0.04)

	#result is dilated for marking the corners, not important
	dst = cv2.dilate(dst,None)

	# Threshold for an optimal value, it may vary depending on the image.
	frame[dst>0.01*dst.max()]=[0,0,255]

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	#time.sleep(0.1)

	# Our operations on the frame come here
	edges = cv2.Canny(gray,100,200)
	blur_gray = cv2.GaussianBlur(edges,(5,5),0)

	#get_text(gray)

	#blur_gray = cv2.GaussianBlur(frame,(5,5),0)
	ret,thresh2 = cv2.threshold(gray,150,255,cv2.THRESH_BINARY_INV)
	# th3 = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
 #            cv2.THRESH_BINARY,15,3)
	# blur_median = cv2.medianBlur(th3,3)
	#final = thresh2 - gray
	#blur_thresh = cv2.GaussianBlur(thresh2,(5,5),0)
	#lower=np.array([220, 220, 0],np.uint8)
	#upper=np.array([255, 255, 255],np.uint8)
	#separated=cv2.inRange(frame,lower,upper)


	#get_text(thresh2)

	#detect_circles(gray)

	draw_corners(thresh2,frame)


	# Display the resulting frame
	cv2.imshow('frame',frame)
	#video_writer.write(frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
#video_writer.release()
cv2.destroyAllWindows()