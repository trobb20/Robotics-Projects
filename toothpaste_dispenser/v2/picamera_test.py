import cv2 as cv
import numpy as np
import time

cap = cv.VideoCapture(0)

def mask_magnitude(mask):
    mask_magnitude = np.sum(mask) / (mask.shape[0] * mask.shape[1]) * (100 / 255)
    return mask_magnitude

lower = np.array([0, 0, 191])
upper = np.array([180, 255, 255])

while True:
    # Take each frame
    _, frame = cap.read()
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, lower, upper)
    mag = mask_magnitude(mask)
    print('Magnitude is %s'%str(mag))

    cv.imshow('frame', frame)
    cv.imshow('mask', mask)

    time.sleep(.25)



