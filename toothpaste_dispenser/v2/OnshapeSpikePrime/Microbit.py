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

code = '''while True: 
	pin0.write_analog(75)
	sleep(1000)
	pin0.write_analog(50)
	sleep(1000)
	pin0.write_analog(100)
	sleep(1000)'''

ser.write(b'\x03')
time.sleep(1)
serial_write(b'from microbit import *')
serial_write(b'display.show(Image.HAPPY)')

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

print(serial_write(b'accelerometer.get_x()'))

while True:
    mates = getMates(client,url,base)
    try:
        monitorValue = serial_write(b'accelerometer.get_x()')
        print('accelerometer value: ' + str(monitorValue[0]))
        for names in mates['mateValues']:
            if names['mateName'] == 'Monitor':
                setMateJSON = names
                if names['jsonType'] == "Revolute":
                    setMateJSON['rotationZ'] = translate(monitorValue[0],-1024,1024,0,2*math.pi)
                elif names['jsonType'] == "Slider":
                    setMateJSON['translationZ'] = translate(monitorValue[0],-1024,1024,0,1)
        setMates(client,url,base,{'mateValues':[setMateJSON]})
        for names in mates['mateValues']:
            if names['mateName'] == 'Control':
                if names['jsonType'] == "Revolute":
                    val = str(math.floor(translate(names['rotationZ'],-math.pi,math.pi,0,9)))
                elif names['jsonType'] == "Slider":
                    val = str(math.floor(translate(names['translationZ'],0,1,0,9)))
        string = 'display.show('+str(val)+')'
        serial_write(string.encode())
    except:
        pass