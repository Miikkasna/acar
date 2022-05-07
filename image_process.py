import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import matplotlib.image as img

#video = cv2.VideoWriter('detections.mp4', 0, 20, (320,280))

dir = 'testdrive3'
for i in range(0, 543, 1):
    img = cv2.imread('{}/{}.jpg'.format(dir, i))
    #img = cv2.imread('testcalib1.jpg')
    if False:
        mutable_object = {} 
        fig = plt.figure()
        def onclick(event):
            print(event.xdata, ',', event.ydata)
            X_coordinate = event.xdata
            Y_coordinate = event.ydata
            mutable_object['click'] = X_coordinate

        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.imshow(img)
        plt.show()
        X_coordinate = mutable_object['click']
    #cv2.imshow('img', img)
    #cv2.waitKey(0)
    pts1 = np.float32([
                        [108, 103], #[148, 169],
                        [217, 101], # [206, 171],
                        [317, 198], # [307, 267],
                        [1, 207] # [9, 269]
                        ])
    pts2 = np.float32([
                        [115, 0],
                        [205, 0],
                        [205, 245],
                        [115, 245]
                        ])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('img', gray)
    #cv2.waitKey(0)
    rows, cols = gray.shape
    M = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(img, M, (cols, rows))

    blur = 7
    blurred = cv2.medianBlur(warped, blur) #cv2.bilateralFilter(gray,10,50,50)
    #cv2.imshow('img', blurred)
    #cv2.waitKey(0)
    minDist = 110
    param1 = 30 #500
    param2 = 8 #200 #smaller value-> more false circles
    minRadius = 6
    maxRadius = 8 #10

    # docstring of HoughCircles: HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]]) -> circles
    circles = cv2.HoughCircles(cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY), cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    mask = np.zeros(img.shape[:2], dtype="uint8")
    M = cv2.getPerspectiveTransform(pts2, pts1)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i, v in enumerate(circles[0,:]):
            cv2.circle(mask, (v[0], v[1]), v[2], 255, -1)
            cv2.putText(mask, (1+i)*'|', (v[0], v[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
        mask = cv2.warpPerspective(mask, M, (cols, rows))
        res = cv2.bitwise_not(img,img,mask = mask)
        cv2.putText(res, 'points: {}'.format(circles.shape[1]), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    else:
        res = img
        cv2.putText(res, 'points: 0', (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    # Show result for testing:
    cv2.imshow('img', res)
    cv2.waitKey(80)
cv2.destroyAllWindows()
