import numpy as np
import cv2
import cv2.cv as cv
import time

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

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
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

	draw_corners(gray,frame)


	cv2.imshow('frame',frame)
	#video_writer.write(frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
#video_writer.release()
cv2.destroyAllWindows()