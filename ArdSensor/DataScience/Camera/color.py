import numpy as np
import cv2
import cv2.cv as cv
import time

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
# fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
# video_writer = cv2.VideoWriter("output.avi", fourcc, 25, (640, 480))
#video_writer = cv2.VideoWriter("output.mp4",cv2.cv.CV_FOURCC('F','M','P', '4'), 15, (640, 480), 1)

def detect_circles(gray):
	#1, src_gray2.rows/8, 200, 20, 0, 0
	#circles = cv2.HoughCircles(gray,cv.CV_HOUGH_GRADIENT, 0.5,10,param1=200,param2=35,minRadius=0,maxRadius=0)
	circles = cv2.HoughCircles(gray,cv.CV_HOUGH_GRADIENT, 0.5,10)
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

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()

	
	img=cv2.GaussianBlur(frame, (5,5), 0)

	#img=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	lower=np.array([200, 200, 0],np.uint8)
	upper=np.array([255, 255, 255],np.uint8)
	separated=cv2.inRange(img,lower,upper)

	cv2.imshow('frame',separated)
	#video_writer.write(frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
#video_writer.release()
cv2.destroyAllWindows()