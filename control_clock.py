import datetime
import logging
from maps_api import google_maps_api_call, return_times_from_api
import time
import RPi.GPIO as GPIO
import numpy as np
import pandas as pd


def traffic_percent(duration: datetime.timedelta, duration_in_traffic: datetime.timedelta):
    logging.debug('Duration seconds: %d' % duration.total_seconds())
    logging.debug('Duration in traffic seconds: %d' % duration_in_traffic.total_seconds())
    return 100 * ((duration_in_traffic.total_seconds() / duration.total_seconds()) - 1)


def mapping_function(x):
    if x <= 0:
        y = 0
    elif x >= 30:
        y = 270
    else:
        y = int(-0.2064 * x ** 2 + 14.818 * x)
    logging.debug('Mapped %s to %s' % (str(x), str(y)))
    return y


def update_traffic_clock(motor, offset, destination):
    """
    Updates the traffic clock depending on a destination (Plus code)
    uses maps_api and duration_math to map a traffic situation to the clock.
    :param motor: buildhat motor object
    :param offset: home position of motor
    :param destination: Plus code of where you want to go (From tufts)
    :return: None
    """
    motor.start(speed=100)  # animation
    response = google_maps_api_call('CV5J+CM Medford, Massachusetts', destination, 'api_key.txt')
    duration, duration_in_traffic = return_times_from_api(response)
    motor_degrees = mapping_function(traffic_percent(duration, duration_in_traffic))
    time.sleep(1)
    motor.stop()
    logging.debug('Moving motor to %s' % (str(motor_degrees)))
    run = offset - motor_degrees
    if run <= -180:
        run = 180 - (abs(run) - 180)
    motor.run_to_position(run, speed=50)


def check_buttons(pins):
    """
    Returns a 2D array of pin states based on GPIO readings

    Ex: [[index, Pin],
         [0, 16],
         [1, 18],
         [0, 22]]

    :param pins: array of board pins to check
    :return: pin_states 2d dataframe
    """
    pin_states = []
    for pin in pins:
        if GPIO.input(pin) == GPIO.HIGH:
            pin_states.append(1)
        elif GPIO.input(pin) == GPIO.LOW:
            pin_states.append(0)
    pin_states = np.array(pin_states)
    pin_df = pd.DataFrame(pins.T, index=pin_states, columns=['Pin'])
    logging.debug('Pin df: %s' % str(pin_df))
    return pin_df
