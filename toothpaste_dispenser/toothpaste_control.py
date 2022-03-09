from buildhat import Motor

mm_per_rev = 18.69
backlash = 2


def extrude_mm(motor: Motor, speed: int, d: float, mm_per_rev: float = mm_per_rev, backlash: float = backlash):
    print('Extruding %f mm...' % d)

    motor.run_for_rotations(d / mm_per_rev, speed=speed)
    motor.run_for_rotations(backlash / mm_per_rev, speed=-speed)
    motor.stop()

    print('Done')
