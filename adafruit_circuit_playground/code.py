# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Edited by Teddy Robbins for use in ME35 at Tufts Univ. 2022

"""This example uses the capacitive touch pads on the Circuit Playground. They are located around
the outer edge of the board and are labeled A1-A6 and TX. (A0 is not a touch pad.) This example
lights up all the NeoPixels a different color of the rainbow for each pad touched!"""
import random
import time
from adafruit_circuitplayground import cp
cp.pixels.brightness = 0.3

# Colors
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

# States
left = ['left', [0, 1, 2, 3, 4]]
right = ['right', [5, 6, 7, 8, 9]]
front = ['front', [3, 4, 5, 6]]
back = ['back', [1, 0, 9, 8]]
all = ['all', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
none = ['none', []]

states = [left, right, front, back, all]

# Loop params
f = 20
correct_answer = True

def get_orientation():
    """
    Returns state based on orientation of board
    :return: state, [name, pixels]
    """
    x, y, z = cp.acceleration
    channel = max(abs(x), abs(y), abs(z))
    if channel == abs(x):
        if x > 0:
            return left
        else:
            return right
    elif channel == abs(y):
        if y > 0:
            return front
        else:
            return back
    elif channel == abs(z):
        if z > 0:
            return none
        else:
            return all

def turn_on_pixels(pixel_color_list):
    """
    Turns on the pixels in pixel_color_list according to their color
    :param pixel_color_list: list of (pixel number, rgb color)
    :return: None
    """
    off = (0, 0, 0)
    pixel_list = [pixel for pixel, color in pixel_color_list]
    off_pixels = [pixel for pixel in all[1] if pixel not in pixel_list]

    for pixel, color in pixel_color_list:
        cp.pixels[pixel] = color
    for pixel in off_pixels:
        cp.pixels[pixel] = off

def random_pixel_choice():
    """
    Gets random pixel choice
    :return: random state name, random pixels to turn on
    """
    random_state = random.choice(states)
    random_state_name = random_state[0]
    random_pixels = random_state[1]
    return random_state_name, random_pixels

# Mainloop
while True:
    # see if user tilted correctly
    if correct_answer:
        name, choice = random_pixel_choice()
        print('Random choice is %s'%name)
        correct_answer = False

    # Get state
    state, on_pixels = get_orientation()
    red_pixels = [pixel for pixel in choice if pixel not in on_pixels]

    prepped_pixels = []
    # Check to see if tilted correctly
    if state == name:
        for pixel in on_pixels:
            prepped_pixels.append((pixel, green))
        print('You got it!')
        correct_answer = True
        turn_on_pixels(prepped_pixels)
        while not state == 'none': #wait for reset
            state, on_pixels = get_orientation()
    else:
        for pixel in on_pixels:
            prepped_pixels.append((pixel, white))
        for pixel in red_pixels:
            prepped_pixels.append((pixel, red))

    turn_on_pixels(prepped_pixels)

    time.sleep(1/f)
