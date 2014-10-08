import numpy as np
import cv2
import cv2.cv as cv
import time

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

#http://opencv-code.com/tutorials/automatic-perspective-correction-for-quadrilateral-objects/

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

	edges = cv2.Canny(gray,100,200,3)
	lines = cv2.HoughLines(edges,1,np.pi/180,130,150) #minLineLength,maxLineGap
	if lines == None:
		continue
	for rho,theta in lines[0]:
		a = np.cos(theta)
		b = np.sin(theta)
		x0 = a*rho
		y0 = b*rho
		extend = 1000
		x1 = int(x0 + extend*(-b))
		y1 = int(y0 + extend*(a))
		x2 = int(x0 - extend*(-b))
		y2 = int(y0 - extend*(a))

		cv2.line(gray,(x1,y1),(x2,y2),(0,0,255),2)

	cv2.imshow('frame',gray)
	#video_writer.write(frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
#video_writer.release()
cv2.destroyAllWindows()