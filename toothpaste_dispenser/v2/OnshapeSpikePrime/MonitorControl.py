from OnshapePlus import *

## Initialize connection to Spike
port = serial_ports()

def serial_write(string):
    ser.write(string + b'\r\n')
    time.sleep(0.1)
    while ser.in_waiting:  
        # print(ser.read(ser.in_waiting).decode())
        response = ser.read(ser.in_waiting).decode()
    result = []
    for s in response.split():
        num = ''
        for x in s:
            # print(x)
            if x.isdigit() or x == "-":
                num += x
        if len(num) > 0:
            result.append(int(num))
    if result == []:
        print(response)
    return result

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
time.sleep(1)

## Beep if connected
ser.write(b'\x03')
time.sleep(0.1)
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
        root.update()
        file_path = filedialog.askopenfilename()
        exec(open(file_path).read())
        base = 'https://cad.onshape.com'
        client = Client(configuration={"base_url": base,
                                    "access_key": access,
                                    "secret_key": secret})
        print('client configured')
        # root.deiconify()
        root.update()
        test = root.destroy()
        print(test)
        # root.quit()
    else:
        access = input('Please enter your access key: ')
        secret = input('Please enter your secret key: ')
        base = 'https://cad.onshape.com'
        client = Client(configuration={"base_url": base,
                                    "access_key": access,
                                    "secret_key": secret})
        print('client configured')

# print()
url = str(input('What is the url of your Onshape assembly? (paste URL then press enter twice): '))

## Bug - url input does not continue after copy paste. placeholder fix for now
placeholder = input()

print('Configure Monitor mode')
defaultPorts = input('Would you like to use the Accelerometer X to control the mate? [y/n]: ')
if defaultPorts == 'y':
    monitorMode = "accel"
else:
    monitorMode = "ultrasonic"
    sensor1Port = input('What port is the ultrasonic sensor in? ')
    serial_write(b'from hub import port')
    sensorString = 'dist_sensor = port.'+sensor1Port+'.device'
    serial_write(sensorString.encode())
    serial_write(b'dist_sensor.mode(0)')

defaultMates = input('Are your mates named "Monitor" and "Control"? [y/n]: ')
if defaultMates == "y":
    controlMate = 'Control'
    monitorMate = 'Monitor'
else:
    controlMate = input('What is the name of the mate you want to control?')
    monitorMate = input('What is the name of the mate you want to use as a monitor?')

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
        if monitorMode == "accel":
            monitorValue = serial_write(b'hub.motion.accelerometer()')
            print('accelerometer value: ' + str(monitorValue[0]))
            for names in mates['mateValues']:
                if names['mateName'] == monitorMate:
                    setMateJSON = names
                    if names['jsonType'] == "Revolute":
                        setMateJSON['rotationZ'] = translate(monitorValue[0],-1024,1024,0,2*math.pi)
                    elif names['jsonType'] == "Slider":
                        setMateJSON['translationZ'] = translate(monitorValue[0],-1024,1024,0,1)
            setMates(client,url,base,{'mateValues':[setMateJSON]})
            # time.sleep(1)
        elif monitorMode == "ultrasonic":
            monitorValue = serial_write(b'dist_sensor.get()')
            try:
                print('ultrasonic sensor value: ' + str(monitorValue[0]))
                for names in mates['mateValues']:
                    if names['mateName'] == monitorMate:
                        setMateJSON = names
                        if names['jsonType'] == "Revolute":
                            setMateJSON['rotationZ'] = translate(monitorValue[0],0,100,0,2*math.pi)
                        elif names['jsonType'] == "Slider":
                            setMateJSON['translationZ'] = translate(monitorValue[0],0,100,0,1)
                setMates(client,url,base,{'mateValues':[setMateJSON]})
            except:
                print('ultrasonic sensor did not give a value')
            # time.sleep(1)
except KeyboardInterrupt:
    controlString = 'hub.port.'+motor1Port+'.pwm(0)'
    serial_write(controlString.encode())