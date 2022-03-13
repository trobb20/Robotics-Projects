from OnshapePlus import *

## Initialize connection to Spike
port = serial_ports()

def serial_write(string):
    ser.write(string + b'\r\n')
    time.sleep(0.1)
    while ser.in_waiting:  
        print(ser.read(ser.in_waiting).decode())

try:
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    print("Port is open")
except:
    serial.Serial(
        port=port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    ).close()
    print("Port is closed")
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    print("Port is open again")

print(ser.isOpen())

## Beep if connected
ser.write(b'\x03')
serial_write(b'import hub')
serial_write(b'hub.sound.beep()')
time.sleep(1)
while ser.in_waiting:  
    ser.read(ser.in_waiting)

serial_write(b'from hub import port')


##
##
## Config Client
try:
    try:
        exec(open('../apikeys.py').read())
        base = 'https://cad.onshape.com'
        client = Client(configuration={"base_url": base,
                                    "access_key": access,
                                    "secret_key": secret})
        print('client configured')
    except:
        exec(open('apikeys.py').read())
        base = 'https://cad.onshape.com'
        client = Client(configuration={"base_url": base,
                                    "access_key": access,
                                    "secret_key": secret})
        print('client configured')
except:
    keyConfig = input('api keys not found, would you like to import keys from a file? [y/n]: ')
    if keyConfig == "y":
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        exec(open(file_path).read())
        base = 'https://cad.onshape.com'
        client = Client(configuration={"base_url": base,
                                    "access_key": access,
                                    "secret_key": secret})
        print('client configured')
    else:
        access = input('Please enter your access key: ')
        secret = input('Please enter your secret key: ')
        base = 'https://cad.onshape.com'
        client = Client(configuration={"base_url": base,
                                    "access_key": access,
                                    "secret_key": secret})
        print('client configured')

url = str(input('What is the url of your Onshape assembly? (paste URL then press enter twice): '))

## Bug - url input does not continue after copy paste. placeholder fix for now
placeholder = input()

defaultPorts = input('Is your motor in port A? [y/n]: ')
if defaultPorts == "y":
    motor1Port = 'A'
    # sensor1Port = 'B'
else:
    motor1Port = input('What port is the motor in? ')
    # sensor1Port = input('What port is the sensor in? ')

controlMode = input('Would you like your assembly mate to control the speed or position of the motor? [speed/position]: ')
def posControl(pos):
    controlString = 'hub.port.'+motor1Port+'.motor.run_to_position('+pos+',speed=50)'
    return controlString
def speedControl(speed):
    controlString = 'hub.port.'+motor1Port+'.pwm('+speed+')'
    return controlString

defaultMates = input('Do you have a mate in your assembly named "Control"? [y/n]: ')
if defaultMates == "y":
    controlMate = 'Control'
    monitorMate = 'Monitor'
else:
    controlMate = input('What is the name of the mate you want to control?')
    # monitorMate = input('What is the name of the mate you want to use as a monitor?')

mates = getMates(client,url,base)
for names in mates['mateValues']:
    print(names['mateName'])

# controlMate = input('What is the name of the mate you want to control your Spike with? ')
# monitorMate = input('What mate do you want the Spike to control? ')

try:
    while True:
        mates = getMates(client,url,base)
        for names in mates['mateValues']:
            if names['mateName'] == controlMate:
                if names['jsonType'] == "Revolute":
                    pos = str(math.floor(translate(names['rotationZ'],0,math.pi,180,0)))
                    speed = str(math.floor(translate(names['rotationZ'],0,2*math.pi,0,255)))
                elif names['jsonType'] == "Slider":
                    pos = str(math.floor(translate(names['translationZ'],0,math.pi,180,0)))
                    speed = str(math.floor(translate(names['translationZ'],0,2*math.pi,0,100)))
        if controlMode == "position":
            string = posControl(pos)
        elif controlMode == "speed":
            string = speedControl(speed)
        serial_write(string.encode())
        time.sleep(1)
except KeyboardInterrupt:
    controlString = 'hub.port.'+motor1Port+'.pwm(0)'
    serial_write(controlString.encode())