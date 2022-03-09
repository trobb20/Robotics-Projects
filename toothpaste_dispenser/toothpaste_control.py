from buildhat import Motor
import numpy as np
import time

mm_per_rev = 18.69
backlash = 2


def extrude_mm(motor: Motor, speed: int, d: float, mm_per_rev: float = mm_per_rev, backlash: float = backlash):
    print('Extruding %f mm...' % d)

    start = motor.get_position()
    motor.run_for_rotations(d / mm_per_rev, speed=speed)
    end = motor.get_position()
    distance_extruded = (start-end)/360 * mm_per_rev
    motor.run_for_rotations(backlash / mm_per_rev, speed=-speed)
    motor.stop()

    print('Done. Extruded %f mm'%distance_extruded)
    return distance_extruded


def home(motor: Motor, speed: int=25):
    print('Homing motor...')
    f = 20
    runtime_max = 3
    ramp_time = 0.5
    backlash = 0.05

    motor.start(speed=speed)
    prev_position = motor.get_position()
    start = time.time()
    while time.time()-start < runtime_max:
        pos = motor.get_position()
        delta = pos-prev_position
        if abs(delta < 5) and time.time()-start > ramp_time:
            break
        prev_position = pos
        time.sleep(1/f)
    motor.stop()
    motor.run_for_rotations(backlash, speed=-speed)
    print('Homed.')
    return


def volume_extruded(d):
    slope = -0.00017067735615326621
    d_m = d/1000
    v_m3 = slope*d_m
    v_mm3 = v_m3*10**9

    return v_mm3