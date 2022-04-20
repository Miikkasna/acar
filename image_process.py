import cv2
import numpy as np
import time
import matplotlib.image as img
import matplotlib.pyplot as plt

t = time.time()

for i in range(1, 400, 2):
    # affine transform
    pts1 = np.float32([
                        [160, 105],
                        [225, 116],
                        [227, 132]
                        ])
    ysift = -80
    xsift = 0
    scale = 1.0
    pts2 = np.float32([
                        [160+xsift, 108+ysift],
                        [204+xsift, 108+ysift],
                        [204+xsift, 178+ysift]
                        ])
    image = cv2.imread('C:\\Users\\miikk\\OneDrive\\Desktop\\images2\\image{}.jpg'.format(i), 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rows, cols = image.shape
    M = cv2.getAffineTransform(pts1, pts2*scale)
    image = cv2.warpAffine(image, M, (cols, rows))



    # Set our filtering parameters
    # Initialize parameter setting using cv2.SimpleBlobDetector
    params = cv2.SimpleBlobDetector_Params()
    
    # Set Area filtering parameters
    params.filterByArea = True
    params.minArea = 40
    
    # Set Circularity filtering parameters
    params.filterByCircularity = True
    params.minCircularity = 0.5
    
    # Set Convexity filtering parameters
    params.filterByConvexity = False
    params.minConvexity = 0.2
        
    # Set inertia filtering parameters
    params.filterByInertia = True
    params.minInertiaRatio = 0.4

    
    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)
        
    # Detect blobs
    keypoints = detector.detect(image)
    
    # Draw blobs on our image as red circles
    blank = np.zeros((1, 1))
    blobs = cv2.drawKeypoints(image, keypoints, blank, (0, 0, 255),
                            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    number_of_blobs = len(keypoints)
    text = "Number of Circular Blobs: " + str(len(keypoints))
    cv2.putText(blobs, text, (20, 550),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)
    # Show blobs
    plt.imshow(blobs)
    plt.pause(0.02)

    #time.sleep(0.02)
print(time.time()-t)
cv2.destroyAllWindows()
