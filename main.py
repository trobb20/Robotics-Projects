from control_clock import *
import logging
import buildhat
import RPi.GPIO as GPIO
import time
import argparse

# Initialization of script
print('Traffic Clock by Teddy Robbins SP2022 Tufts Univ.')
parser = argparse.ArgumentParser()
parser.add_argument('-lf', '--logfile', default='log_%s.txt' % (str(time.time())))
parser.add_argument('-l', '--logging_level', default='ERROR')
parser.add_argument('-m', '--motor_port', default='A')
parser.add_argument('-o', '--offset', default=-45, type=int)
parser.add_argument('-f', '--frequency', default=10, type=int)
args = parser.parse_args()

print('Parsing args...')
if str(args.logging_level) == 'DEBUG':
    logging.basicConfig(filename=args.logfile, level=logging.DEBUG)
else:
    logging.basicConfig(filename=args.logfile, level=logging.ERROR)

print('Initializing...')
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
traffic_motor = buildhat.Motor(args.motor_port)
offset = args.offset  # Resting location of the motor at 0% traffic.
f = args.frequency  # refresh rate

# Use pins GPIO 23, 24, 25 aka BOARD 16, 18, 22

destinations = np.array([
    'Q257+5Q Manhattan, New York, NY',  # Times Square
    'J6G3+G7 Killington, Vermont',  # Killington Ski Area
    'WXHC+X7 Wellfleet, Massachusetts'  # Wellfleet on the Cape
], dtype=np.dtype(str))

pins = np.array([
    16,
    18,
    22
], dtype=np.dtype(int))

button_map = pd.DataFrame(destinations.T, index=pins, columns=['Location'])
for pin in pins:
    GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print('Homing system...')
# Initialize system
traffic_motor.run_to_position(offset)  # home system

print('Beginning mainloop. Press 2 buttons to exit.')
# Mainloop
while True:
    pin_df = check_buttons(pins)
    if sum(pin_df.index) == 1:
        # A single button is turned on, check which one
        pin_pressed = pin_df.loc[1]['Pin']
        logging.debug('Pressed pin: %s' % str(pin_pressed))
        update_traffic_clock(traffic_motor, offset, button_map.loc[pin_pressed]['Location'])
    elif sum(pin_df.index) == 2:
        # multiple buttons are pressed, exit the program.
        break
    else:
        # no buttons pressed
        pass
    time.sleep(1 / f)

print('Exited loop.')
exit()
