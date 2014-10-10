## Color Tracking v1.0
## Copyright (c) 2013-2014 Abid K and Jay Edry
## You may use, redistribute and/or modify this program it under the terms of the MIT license (https://github.com/abidrahmank/MyRoughWork/blob/master/license.txt).


''' v 0.1 - It tracks two objects of blue and yellow color each '''

import cv2
import numpy as np
import files
from pytesseract import image_to_string
from PIL import Image

def get_text(frame):
    arr = np.array(frame)
    img = Image.fromarray(arr)
    print(image_to_string(img))


def nothing(x):
    print x
    pass
# Create a black image, a window
cv2.namedWindow('image')

# create trackbars for color change
cv2.createTrackbar('var1','image',63,255,nothing)
cv2.createTrackbar('var2','image',150,255,nothing)

# Hue  = actual color range
# Sat = Intensity - 0 for white
# Value = Brightness, 0 is black
# In OpenCV, H = 0-180, S = 0-255, V = 0-255
def getthresholdedimg(hsv):
    yellow = cv2.inRange(hsv,np.array((20,100,100)),np.array((30,255,255)))
    blue = cv2.inRange(hsv,np.array((100,100,10)),np.array((120,255,255)))
    both = cv2.add(yellow,blue)
    return both

#c = cv2.VideoCapture(0)
#c.set(3,800)
#c.set(4,600)
#width,height = c.get(3),c.get(4)
#print "frame width and height : ", width, height

img = cv2.imread('school.jpg')

while(1):


    # Variables to play
    var1 = cv2.getTrackbarPos('var1','image')
    var2 = cv2.getTrackbarPos('var2','image')

    #_,f = c.read()
    f = img
    f = cv2.flip(f,1)
    blur = cv2.medianBlur(f,5)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    both = getthresholdedimg(hsv)
    erode = cv2.erode(both,None,iterations = 3)
    dilate = cv2.dilate(erode,None,iterations = 10)

    res = cv2.bitwise_and(f,f, mask= erode)

    contours,hierarchy = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        cx,cy = x+w/2, y+h/2
        
        # # Detect yellow
        # if 20 < hsv.item(cy,cx,0) < 30:
        #     cv2.rectangle(f,(x,y),(x+w,y+h),[0,255,255],2)
        #     #print "yellow :", x,y,w,h

        # Detect Blue
        if 100 < hsv.item(cy,cx,0) < 120:
            f_copy = np.copy(f)
            cv2.rectangle(f,(x,y),(x+w,y+h),[255,0,0],2)

            # Crop image
            crop_img = f_copy[y:y+h+30, x:x+w]
            resized = cv2.resize(crop_img, (0,0), fx=4, fy=4) 
            edges = cv2.Canny(resized,var1,38,3)


            # Image Corners
            # gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)
            # gray = np.float32(edges)
            # dst = cv2.cornerHarris(gray,2,3,0.04)
            # dst = cv2.dilate(dst,None)
            # resized[dst>0.01*dst.max()]=[0,0,255]

            # # SIFT?

            # Get hough lines
            lines = cv2.HoughLines(edges,1,np.pi/180,63,150) #minLineLength,maxLineGap
            #lines = cv2.HoughLines(edges,1,np.pi/180,63,150) #minLineLength,maxLineGap
            if lines == None:
                print "NO LINES"
                continue

            # Iterate and get values
            line_arr = files.get_lines(lines)
            for line in line_arr:
                cv2.line(edges,(line.x1,line.y1),(line.x2,line.y2),(255,255,0),3)

            # Get points
            height, width = edges.shape
            point_arr = files.get_points(line_arr,raw=1, binned_x=1, binned_y=0, variance=0.1)
            cpoint_arr = [[0,0],[width,0],[width,height],[0,height]]
            corner_points = []
            
            # Find 4 corner points
            #print point_arr
            if len(point_arr) < 4:
                cv2.imshow('test',edges)
                print "Too few points 1"
                break
            for i,cpoint in enumerate(cpoint_arr):
                minDistance = 100000
                currMinPoint = [0,0]
                for point in point_arr:
                    if (point[0] > width) or  (point[0] < 0) or (point[1] > height) or  (point[1] < 0):
                        continue
                    #cv2.circle(edges,(point[0],point[1]),5,(255,255,255),2)
                    currDist = files.distance_between_points(cpoint,point)
                    if currDist < minDistance:
                        minDistance = currDist
                        currMinPoint = [point[0],point[1]]
                if currMinPoint != None:
                    if len(corner_points) > 0:
                        if not (corner_points[-1][0]==currMinPoint[0] and corner_points[-1][1]==currMinPoint[1]):
                            corner_points.append(currMinPoint)
                            cv2.circle(edges,(currMinPoint[0],currMinPoint[1]),5,(0,255,0),2)
                    else:
                        corner_points.append(currMinPoint)
                        cv2.circle(edges,(currMinPoint[0],currMinPoint[1]),5,(0,255,0),2)

            # Find the 4 cornermost points
            print corner_points
            if len(corner_points) < 4:
                cv2.imshow('test',edges)
                print "Too few points 2"
                break
            defined_corners = files.get_corners(corner_points)
            src = np.array([defined_corners["tl"],defined_corners["tr"],defined_corners["bl"],defined_corners["br"]],np.float32)
            dst = np.array([[0,0],[width,0],[0,height],[width,height]],np.float32)

            # Warp image to perspective
            M = cv2.getPerspectiveTransform(src,dst)
            dst = cv2.warpPerspective(resized,M,(width,height))
            #dst_edge = cv2.Canny(dst,68,38,3)
            
            print get_text(dst)
            cv2.imshow('test',edges)
            #print "blue :", x,y,w,h

    cv2.imshow('img',f)

    if cv2.waitKey(25) == 27:
        break

cv2.destroyAllWindows()
#c.release()