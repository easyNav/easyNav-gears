import cv2
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

retval, img = cap.read()

cv2.imwrite('01.png',img)

cap.release()