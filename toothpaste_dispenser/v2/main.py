from toothpaste_control2 import *

paste_motor = Motor('C')
brush_motor = Motor('D')
base = 'https://cad.onshape.com'
url = 'https://cad.onshape.com/documents/e61d2284326681e60c354303/w/06c3440ad86b926c4800c9f0/e/dbe6eb65c9ad4e1b46e8850b'
client = configure_client('OnshapeSpikePrime/apikeys.txt')


# PARAMETERS
f = 4           # hz to run at
buffer_length = 2 * f # seconds of buffer
buffer = np.zeros(buffer_length)


print('Homing system.')
home(paste_motor)
pos = 0

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.framerate = 24
    time.sleep(2)
    print('Initialized Camera.')
    time.sleep(.25)

    toothbrush_no_paste = calibrate_blue(camera, 3)

    try:
        print('Starting mainloop...')
        while True:
            np.roll(buffer, 1)
            buffer[0] = capture_blue(camera)/toothbrush_no_paste - 1
            print(buffer)
            event = detect_event(buffer)
            if event == 'toothpaste':
                print('I see toothpaste!')
            elif event == 'no brush':
                print('Brush unloaded!')

            update_model(pos, client, url, base)
            time.sleep(1/f)



    except KeyboardInterrupt:
        paste_motor.stop()
        brush_motor.stop()
        print('Done.')
        exit()
