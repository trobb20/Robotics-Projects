import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import picamera
from toothpaste_control2 import *

brush_lower = np.array([0, 0, 255 / 2])
brush_upper = np.array([0, 255 / 2, 255])
paste_lower = np.array([160 / 2, 50, 50])
paste_upper = np.array([255 / 2, 255, 255])

with picamera.PiCamera() as camera:
    # Initialize camera
    camera.resolution = (320, 240)
    camera.framerate = 24
    time.sleep(2)
    print('Initialized Camera.')
    time.sleep(.25)

    try:
        print('Starting mainloop...')
        while True:
            # Grab an image and detect the event associated with it
            img = capture_and_crop(camera)
            percentage = percent_color_in_image(img, brush_lower, brush_upper, show_mask=True)
            print(percentage)
            time.sleep(.25)

    except KeyboardInterrupt:
        print('Done.')
        exit()