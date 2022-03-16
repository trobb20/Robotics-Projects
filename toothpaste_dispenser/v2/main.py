from toothpaste_control2 import *
from buildhat import ForceSensor

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
brush_motor_out_rotations = -1.5
brush_timeout_s = 3
brush_lower = np.array([0, 0, 255 / 2])
brush_upper = np.array([0, 255 / 2, 255])
paste_lower = np.array([160 / 2, 0, 0])
paste_upper = np.array([255 / 2, 255, 255])

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

    print('Ready to load brush!')
    # Move brush out for loading
    brush_motor.run_for_rotations(brush_motor_out_rotations, speed=10)

    try:
        print('Starting mainloop...')
        while True:
            # Grab an image and detect the event associated with it
            img = capture_and_crop(camera)
            event = detect_event(img, brush_lower, brush_upper, paste_lower, paste_upper)

            # State machine
            if event == 'paste':
                print('I see toothpaste!')
                # Take a photo of toothpaste and unload brush
                time.sleep(1)
                print('Taking photo...')
                camera.capture('toothpaste.jpg')
                time.sleep(1)

                print('Unloading brush...')
                home(paste_motor)
                brush_motor.run_for_rotations(brush_motor_out_rotations, speed=25)
                print('%f mm3 of toothpaste remain.'%volume)

                extruding = False
                loaded = False
                continue

            elif not loaded and event is None:
                print('No brush... Press button to load.')
                # when button pressed, home the brush motor to check if its loaded
                while not button.is_pressed():
                    pass
                home(brush_motor)
                time.sleep(1)
                loaded = True
                continue

            elif loaded and event is None:
                print('Brush did not load. Press button to try again...')
                # when button pressed, home the brush motor to check if its loaded
                while not button.is_pressed():
                    pass
                home(brush_motor)
                continue

            elif not extruding and event == 'brush':
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
                continue

            elif extruding and event == 'brush':
                if brush_timeout_count / f > brush_timeout_s:
                    print('Brush timeout! No paste was extruded.')
                    extruding = False
                    brush_timeout_count = 0
                else:
                    brush_timeout_count = brush_timeout_count + 1
                continue

            time.sleep(1 / f)

    except KeyboardInterrupt:
        paste_motor.stop()
        brush_motor.stop()
        print('Done.')
        exit()
