from toothpaste_control import *
import time

motor = Motor('A')
base = 'https://cad.onshape.com'
url = 'https://cad.onshape.com/documents/e61d2284326681e60c354303/w/06c3440ad86b926c4800c9f0/e/dbe6eb65c9ad4e1b46e8850b'
client = configure_client('../OnshapeSpikePrime/apikeys.txt')

print('Homing system.')
home(motor)
pos = 0

try:
    while True:
        new_pos = update_model(motor, pos, client, url, base)
        pos = new_pos
        time.sleep(1)

except KeyboardInterrupt:
    motor.stop()
    print('Done.')