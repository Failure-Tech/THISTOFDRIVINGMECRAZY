import usb.util
import usb.core

import os

os.environ['PYUSB_DEBUG'] = 'debug'

def grabTOF(): 
    
    device = usb.core.find(idVendor = 0x276e, idProduct = 0x0301)

    if device is None:
        print("No device found.")

        return None

    return device

def decodeResponse(response):

    numList = response

    string = ""

    for num in numList:

        byte = num.to_bytes(1, 'little')

        character = byte.decode('ascii')
        
        print(byte, " char: ", character)

        string = string + character
    
    return string

# get de
TOFSensor = grabTOF()  

TOFSensor.set_configuration()

config = TOFSensor.get_active_configuration()

interface = config[(0, 0)]

OUT = interface[1]
IN = interface[0]

# print(config)

try:
    TOFSensor.set_interface_altsetting(interface = 0, alternate_setting = 0)
except:
    pass

msg = b"test"

print(OUT, "\n", IN)

try:

    TOFSensor.write(OUT.bEndpointAddress, b"\x57\x57")
    print("hello")

    rawResponse = TOFSensor.read(IN.bEndpointAddress, 4, 14000)
    print("1738")

    interpretedResponse = decodeResponse(rawResponse)

    print("Response: ", interpretedResponse)

except:
    pass


usb.util.dispose_resources(TOFSensor)

# TOFSensor.reset()