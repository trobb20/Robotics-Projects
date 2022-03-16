import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import random


def percent_color_in_image(img, lower_bound, upper_bound, show_mask=False, img_fmt=cv.COLOR_RGB2HSV):
    """
    Gets the percent of an image that is within a certain hsv color range spanned
    by lower_bound and upper bound
    :param img_fmt: format of image to convert to HSV as opencv object. Default is RGB
    :param img: image (RGB format) to analyze
    :param lower_bound: hsv vector lower bound
    :param upper_bound: hsv vector upper bound
    :param show_mask: optional argument to show the img mask using matplotlib
    :return: float percentage of image in color bounds
    """
    img = cv.cvtColor(img, img_fmt)
    mask = cv.inRange(img, lower_bound, upper_bound)
    if show_mask:
        plt.imshow(cv.cvtColor(mask, cv.COLOR_BGR2RGB))
        plt.show()
    percentage = mask_magnitude(mask)
    return percentage


def mask_magnitude(mask):
    """
    Computes the percentage of a mask that is "on"
    :param mask: image mask of either 0,0,0 values or 255,255,255 values
    :return: magnitude (or percentage) of pixels that are on
    """
    magnitude = np.sum(mask) / (mask.shape[0] * mask.shape[1]) * (100 / 255)
    return magnitude


nothing = [cv.imread('nothing.png'), 'nothing']
brush = [cv.imread('brush.png'), 'brush']
paste = [cv.imread('paste.png'), 'paste']

imgs = [nothing, brush, paste]

def run_trial(imgs):
    recognize_thresh = 5

    brush_lower = np.array([0, 0, 255/2])
    brush_upper = np.array([0, 255/2, 255])

    paste_lower = np.array([160/2, 50, 50])
    paste_upper = np.array([255/2, 255, 255])

    #print('##################################')
    img_pack = random.choice(imgs)
    img = img_pack[0]
    name = img_pack[1]
    #print('Analyzing %s'%name)

    print('Checking for brush: ')
    brush_amt = percent_color_in_image(img, brush_lower, brush_upper)
    print('%f percent brush'%brush_amt)

    print('Checking for paste: ')
    paste_amt = percent_color_in_image(img, paste_lower, paste_upper)
    print('%f percent paste' % paste_amt)

    if brush_amt + paste_amt < recognize_thresh:
        guess = 'nothing'
    else:
        if paste_amt < recognize_thresh:
            guess = 'brush'
        else:
            guess = 'paste'

    if guess == name:
        return 1
    else:
        return 0

count = 0
for i in range(100):
    count = count + run_trial(imgs)

print(count)