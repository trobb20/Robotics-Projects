from toothpaste_control2 import *

# DECLARATIONS
paste_motor = Motor('C')
brush_motor = Motor('D')
button = ForceSensor('A')
base = 'https://cad.onshape.com'
url = 'https://cad.onshape.com/documents/e61d2284326681e60c354303/w/06c3440ad86b926c4800c9f0/e/dbe6eb65c9ad4e1b46e8850b'
client = configure_client('OnshapeSpikePrime/apikeys.txt')
extruding = False
loaded = False
pos = 0
volume = 0
extrude = 0
brush_timeout_count = 0

# PARAMETERS
f = 4  # hz to run at
buffer_length = 1 * f  # seconds of buffer
buffer = np.zeros(buffer_length)
brush_motor_out_rotations = -1.5
brush_timeout_s = 3

# INIT
print('Preparing system.')
home(paste_motor)
home(brush_motor)

# MAINLOOP
with picamera.PiCamera() as camera:
    # Initialize camera
    camera.resolution = (320, 240)
    camera.framerate = 24
    time.sleep(2)
    print('Initialized Camera.')
    time.sleep(.25)

    # Calibrate toothbrush values
    toothbrush_no_paste = calibrate_blue(camera, 3)

    # Move brush out for loading
    brush_motor.run_for_rotations(brush_motor_out_rotations, speed=10)

    try:
        print('Starting mainloop...')
        while True:
            # Update camera buffer and check events
            buffer = np.roll(buffer, 1)
            buffer[0] = capture_blue(camera) / toothbrush_no_paste - 1
            event = detect_event(buffer)

            # State machine
            if event == 'toothpaste':
                print('I see toothpaste!')
                # Take a photo of toothpaste and unload brush
                time.sleep(1)
                print('Taking photo...')
                camera.capture('toothpaste.jpg')
                time.sleep(1)

                print('Unloading brush...')
                brush_motor.run_for_rotations(brush_motor_out_rotations, speed=25)
                print('%f mm3 of toothpaste remain.'%volume)

                extruding = False
                loaded = False

            elif not loaded and event == 'no brush':
                print('No brush... Press button to load.')
                # when button pressed, home the brush motor to check if its loaded
                while not button.is_pressed():
                    pass
                loaded = True
                home(brush_motor)

            elif not extruding and event is None:
                print('Brush inserted and ready for toothpaste! Press button to extrude.')
                # wait for button press
                while not button.is_pressed():
                    pass
                extruding = True
                extrude = extrude_mm(paste_motor, -20, 10)
                pos = pos + extrude
                volume = volume + volume_extruded(extrude)
                update_model(pos, client, url, base)
                extrude = 0

            elif extruding and event is None:
                if brush_timeout_count / f > brush_timeout_s:
                    print('Brush timeout! No paste was extruded.')
                    extruding = False
                    brush_timeout_count = 0
                else:
                    brush_timeout_count = brush_timeout_count + 1

            time.sleep(1 / f)

    except KeyboardInterrupt:
        paste_motor.stop()
        brush_motor.stop()
        print('Done.')
        exit()
