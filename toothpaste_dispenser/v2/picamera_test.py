import time
import picamera
import numpy as np
import matplotlib.pyplot as plt
from toothpaste_control2 import *

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.framerate = 24
    time.sleep(2)
    print('Initialized Camera.')
    toothbrush = calibrate_blue(camera, 5)
    print(toothbrush)

    x = []
    values = []

    plt.figure()

    for i in range(4*10):
        x.append(i)
        values.append(capture_blue(camera)/toothbrush - 1)
        plt.plot(x, values)
        plt.show()
        plt.pause(0.25)

