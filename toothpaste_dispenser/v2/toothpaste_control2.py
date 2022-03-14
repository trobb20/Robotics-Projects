from buildhat import Motor, ForceSensor
from OnshapeSpikePrime.OnshapePlus import *
import picamera
import numpy as np
import time

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


def capture_blue(camera, x_range = (20, 200), y_range = (65, 165)):
    output = np.empty((240, 320, 3), dtype=np.uint8)
    camera.capture(output, 'rgb')
    cropped = output[x_range[0]:x_range[1], y_range[0]:y_range[1], :]
    r = np.mean(cropped[:, :, 0])
    b = np.mean(cropped[:, :, 1])
    g = np.mean(cropped[:, :, 2])

    n = ((r + g - b) / ((r + b + g) / 3))

    return n


def calibrate_blue(camera, t: int, f = 4):
    print('Calibrating for %s seconds...'%str(t))
    normalized_values = np.empty((t*f))
    for i in range(int(t*f)):
        normalized_values[i] = capture_blue(camera)
        time.sleep(1/f)

    return np.mean(normalized_values)


def detect_event(buffer, no_brush_thresh = 0.02, toothpaste_thresh = -0.05):
    if np.mean(buffer) < toothpaste_thresh:
        return 'toothpaste'
    elif np.mean(buffer) > no_brush_thresh:
        return 'no brush'
    else:
        return None
