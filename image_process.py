import numpy as np
import cv2

# define points for top view perspective transform
pts1 = np.float32([
                    [108, 103],
                    [217, 101],
                    [317, 198],
                    [1, 207]
                    ])
pts2 = np.float32([
                    [115, 0],
                    [205, 0],
                    [205, 245],
                    [115, 245]
                    ])

# initialize computer vision parameters. Will be overwritten by web server parameters.
params = {
    'anchors' : 3,
    'blur' : 7,
    'mindist' : 80, # min dist between found circles
    'param1' : 30, 
    'threshold' : 9, # smaller value-> more false circles
    'minradius' : 6,
    'maxradius' : 8
}

def update_params(string_params_dict):
    global params
    for key in string_params_dict.keys():
        params[key] = int(string_params_dict[key])

def process_image(img):
    # define image shape and center
    h, w, _ = img.shape
    c = int(w/2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows, cols = gray.shape
    M = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(img, M, (cols, rows))
    blurred = cv2.medianBlur(warped, params['blur'])
    
    circles = cv2.HoughCircles(cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY), cv2.HOUGH_GRADIENT, 1, params['mindist'], param1=params['param1'], param2=params['threshold'], minRadius=params['minradius'], maxRadius=params['maxradius'])
    mask = np.zeros(img.shape[:2], dtype="uint8")
    M = cv2.getPerspectiveTransform(pts2, pts1)
    x, y = c, 1
    target = (x, y)
    if circles is not None:
        circles = np.uint16(np.around(circles))[0,:params['anchors']] # take slice of best points
        for i, v in enumerate(circles):
            cv2.putText(mask, (1+i)*'|', (v[0], v[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
        weights = [2, 1, 1, 1, 1][:circles.shape[0]]
        x = np.average(circles[:, 0], weights=weights)
        y = np.average(circles[:, 1], weights=weights)
        target = (int(x), int(y))
        mask = cv2.warpPerspective(mask, M, (cols, rows))
        res = cv2.bitwise_not(img,img,mask = mask)
        cv2.arrowedLine(res, (c, h), target, (0, 200, 0), thickness=2)
    else:
        res = img

    dx, dy = c - x, h - y
    angle = round(np.degrees(np.tan(dx/(dy+1))), 1)
    if abs(angle) > 90: angle = 0

    # wrap extracted features
    fts = {'direction_angle': angle}

    return res, fts

