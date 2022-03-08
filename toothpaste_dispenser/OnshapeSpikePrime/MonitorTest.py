from OnshapePlus import *

## Initialize connection to Spike
port = serial_ports()


def serial_write(string):
    ser.write(string + b'\r\n')
    time.sleep(0.1)
    while ser.in_waiting:  
        # print(ser.read(ser.in_waiting).decode())
        response = ser.read(ser.in_waiting).decode()
    print(response)
    result = []
    for s in response.split():
        num = ''
        for x in s:
            # print(x)
            if x.isdigit() or x == "-":
                num += x
        if len(num) > 0:
            result.append(int(num))
    return result

try:
    ser = serial.Serial(
        port=port, 
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
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
serial_write(b'dist_sensor = port.A.device')
accel = serial_write(b'hub.motion.accelerometer()')
print('value:')
print(accel)
serial_write(b'dist_sensor.mode(0)')
ultrasonic = serial_write(b'dist_sensor.get()')
print(ultrasonic)
while True:
    ultrasonic = serial_write(b'dist_sensor.get()')
    print(ultrasonic)
    time.sleep(1)
# serial_write(sensorSetup.encode())
# print(distance)