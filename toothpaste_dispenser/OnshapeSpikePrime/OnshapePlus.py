from os import access
import time
import math
import serial
import sys
import glob
import json
try:
    import tkinter as tk
    from tkinter import filedialog
except:
    print('tkinter not installed - cannot import apikeys from file with gui')

from onshape_client.client import Client
from onshape_client.onshape_url import OnshapeElement

##
##
## Define Serial Functions
##
##
def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
        for port in ports:
            if 'usb' in port:
                guess = port                
                
        try:
            return guess
        except:
            print('no USB ports found')
            quit()
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    print('port found:'+result[0])
    return result[0]

##
##
## Config Onshape Client
##
##

def configClientWithKeys():
    access = input("what is your access key?: ")
    secret = input("what is your secret key?: ")
    base = 'https://cad.onshape.com'
    client = Client(configuration={"base_url": base,
                                "access_key": access,
                                "secret_key": secret})
    print('client configured')
    return client

##
##
## Onshape Functions
##
##

## Get Mates Function
def getMates(client,url,base):
    fixed_url = '/api/assemblies/d/did/w/wid/e/eid/matevalues'
    element = OnshapeElement(url)
    method = 'GET'

    params = {}
    payload = {}
    headers = {'Accept': 'application/vnd.onshape.v2+json',
                'Content-Type': 'application/vnd.onshape.v2+json'}

    fixed_url = fixed_url.replace('did', element.did)
    fixed_url = fixed_url.replace('wid', element.wvmid)
    fixed_url = fixed_url.replace('eid', element.eid)

    response = client.api_client.request(method, url=base + fixed_url, query_params=params, headers=headers, body=payload)

    parsed = json.loads(response.data)
    # The command below prints the entire JSON response from Onshape
    # print(json.dumps(parsed, indent=4, sort_keys=True))
    return parsed

def setMates(client,url,base,body):
    fixed_url = '/api/assemblies/d/did/w/wid/e/eid/matevalues'
    element = OnshapeElement(url)
    method = 'POST'

    params = {}
    payload = body
    headers = {'Accept': 'application/vnd.onshape.v2+json',
                'Content-Type': 'application/vnd.onshape.v2+json'}

    fixed_url = fixed_url.replace('did', element.did)
    fixed_url = fixed_url.replace('wid', element.wvmid)
    fixed_url = fixed_url.replace('eid', element.eid)

    response = client.api_client.request(method, url=base + fixed_url, query_params=params, headers=headers, body=payload)

    parsed = json.loads(response.data)
    # The command below prints the entire JSON response from Onshape
    # print(json.dumps(parsed, indent=4, sort_keys=True))
    return parsed

## Mass Prop test
def massProp(client, url: str, base):
  fixed_url = '/api/partstudios/d/did/w/wid/e/eid/massproperties'
  element = OnshapeElement(url)
  method = 'GET'

  params = {}
  payload = {}
  headers = {'Accept': 'application/vnd.onshape.v1+json; charset=UTF-8;qs=0.1',
            'Content-Type': 'application/json'}

  fixed_url = fixed_url.replace('did', element.did)
  fixed_url = fixed_url.replace('wid', element.wvmid)
  fixed_url = fixed_url.replace('eid', element.eid)

  response = client.api_client.request(method, url=base + fixed_url, query_params=params, headers=headers, body=payload)
  print(response.status)
  print(response.data)
  parsed = json.loads(response.data)
  # The command below prints the entire JSON response from Onshape
  print(json.dumps(parsed, indent=4, sort_keys=True))
  return parsed


##
##
## Helper Functions
##
##
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)