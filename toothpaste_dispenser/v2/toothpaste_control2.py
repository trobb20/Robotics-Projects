from buildhat import Motor
from OnshapeSpikePrime.OnshapePlus import *
import picamera
import cv2 as cv
import numpy as np
import time
import matplotlib.pyplot as plt

mm_per_rev = 18.69
backlash = 2


def configure_client(api_path, base='https://cad.onshape.com'):
    """
    Returns an onshape client object given API keys path and a base url
    :param api_path: path to a file with access, secret keys
    :param base: base url for onshape
    :return: Onshape Client
    """
    try:
        access, secret = open(api_path).readlines()
        client = Client(configuration={"base_url": base,
                                       "access_key": access.strip('\n'),
                                       "secret_key": secret})
        print('client configured')
    except Exception as e:
        print(e)
        return

    return client


def extrude_mm(motor: Motor, speed: int, d: float, mm_per_rev: float = mm_per_rev, backlash: float = backlash):
    """
    Extrudes toothpaste based on a distance in mm
    :param motor: buildhat Motor object
    :param speed: speed % to run at
    :param d: distance in mm to extrude
    :param mm_per_rev: mm per revolution of motor
    :param backlash: amount to back off to let pressure reduce on toothpaste
    :return: returns the real distance extruded as calculated by the motor
    """
    print('Extruding %f mm...' % d)

    start = motor.get_position()
    motor.run_for_rotations(d / mm_per_rev, speed=speed)
    motor.run_for_rotations(backlash / mm_per_rev, speed=-speed)
    end = motor.get_position()
    distance_extruded = (start - end) / 360 * mm_per_rev
    motor.stop()

    print('Done. Extruded %f mm' % distance_extruded)
    return distance_extruded


def home(motor: Motor, speed: int = 25):
    """
    Homes motor until it feels a hard object
    :param motor: buildhat Motor object
    :param speed: speed at which to home
    :return: none
    """
    print('Homing motor...')
    f = 20  # frequency to check position
    runtime_max = 3  # max time to search for home
    ramp_time = 0.5  # grace period at start of homing sequence
    backlash = 0.05  # rotations to back off from hard object

    motor.start(speed=speed)
    prev_position = motor.get_position()
    start = time.time()
    while time.time() - start < runtime_max:
        pos = motor.get_position()
        delta = pos - prev_position
        if abs(delta < 2) and time.time() - start > ramp_time:
            break
        prev_position = pos
        time.sleep(1 / f)
    motor.stop()
    motor.run_for_rotations(backlash, speed=-speed)
    print('Homed.')
    return


def volume_extruded(d):
    """
    Based on a distance extruded, calculates amount of toothpaste extruded
    :param d: distance extruded in mm
    :return: volume of toothpaste in mm3
    """
    slope = -0.00017067735615326621
    d_m = d / 1000
    v_m3 = slope * d_m
    v_mm3 = v_m3 * 10 ** 9

    return v_mm3


def update_model(current_pos: float, client, url, base):
    """
    Compares onshape model to real life and updates onshape model
    :param motor: buildhat Motor object
    :param current_pos: current position of slider wrt home in mm
    :param client: onshape client
    :param url: assembly url
    :param base: base url
    :return: True if success
    """
    mate_pos = None
    control_mate = None

    # Get mate position
    for mate in getMates(client, url, base)['mateValues']:
        if mate['mateName'] == 'Control':
            control_mate = mate
            mate_pos = -mate['translationZ'] * 1000 - 6
            print('Position of slider: %f' % mate_pos)

    # Update mate position
    if control_mate is not None:
        set_mate_JSON = control_mate
    else:
        print('Error finding mate.')
        return False

    set_mate_JSON['translationZ'] = (-current_pos - 6) / 1000
    setMates(client, url, base, {'mateValues': [set_mate_JSON]})
    print('Set new position to current: %f' % current_pos)

    return True


def capture_and_crop(camera, x_range=(20, 200), y_range=(65, 165)):
    """
    Captures a photo on picamera camera and returns cropped image in
    x_range and y_range
    :param camera: picamera camera
    :param x_range: tuple of min, max pixels in x
    :param y_range: tuple of min, max pixels in y
    :return: cropped image
    """
    output = np.empty((240, 320, 3), dtype=np.uint8)
    camera.capture(output, 'rgb')
    cropped = output[x_range[0]:x_range[1], y_range[0]:y_range[1], :]
    return cropped


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
    # Perform opening to reduce noise
    kernel = np.ones((10, 10), np.uint8)
    opening = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

    if show_mask:
        plt.imshow(cv.cvtColor(opening, cv.COLOR_BGR2RGB))
        plt.show()

    percentage = mask_magnitude(opening)
    return percentage


def mask_magnitude(mask):
    """
    Computes the percentage of a mask that is "on"
    :param mask: image mask of either 0,0,0 values or 255,255,255 values
    :return: magnitude (or percentage) of pixels that are on
    """
    magnitude = np.sum(mask) / (mask.shape[0] * mask.shape[1]) * (100 / 255)
    return magnitude


def detect_event(img, brush_lower, brush_upper, paste_lower, paste_upper, detection_thresh=25):
    """
    Compares an image of a toothbrush with hsv bounds for paste and brush
    Returns if it believes it sees a brush or it sees paste
    :param img: image to assess
    :param brush_lower: lower bound for toothbrush hsv
    :param brush_upper: upper bound for toothbrush hsv
    :param paste_lower: lower bound for paste hsv
    :param paste_upper: upper bound for paste hsv
    :param detection_thresh: percentage of color that has to be in image for it to be detected
    :return:
    """
    # Brighten image to check for brush
    high_c = cv.convertScaleAbs(img, alpha=2)

    # Saturate image to check for paste
    high_s = cv.cvtColor(img, cv.COLOR_RGB2HSV)
    high_s[:, :, 1] = 255
    high_s = cv.cvtColor(high_s, cv.COLOR_HSV2RGB)

    brush_amt = percent_color_in_image(high_c, brush_lower, brush_upper)
    print('%f percent brush' % brush_amt)

    paste_amt = percent_color_in_image(high_s, paste_lower, paste_upper)
    print('%f percent paste' % paste_amt)

    if brush_amt + paste_amt < detection_thresh:
        guess = None
    else:
        if paste_amt < detection_thresh:
            guess = 'brush'
        else:
            guess = 'paste'

    return guess
