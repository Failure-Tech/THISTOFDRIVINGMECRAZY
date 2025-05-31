import usb.util
import usb.core

device = usb.core.find(idVendor = 0x276e, idProduct = 0x0301)

if device is None:
    print("No device found.")
 

device.set_configuration()

config = device.get_active_configuration()

interface = config[(0, 0)]

OUT = interface[1]
IN = interface[0]

msg = b'\0\x02\0\x03\0\x04'

usb.util.claim_interface(device, 0)

print(device)

try:

    device.write(0x81, msg, 5000)
    #assert TOFSensor.write(0x81, msg, 1000) == len(msg)
    rawResponse = device.read(0x01, 32, 5000)

# interpretedResponse = decodeResponse(rawResponse)

    print("Response: ", rawResponse)

except:
    pass

# usb.util.dispose_resources(device)
usb.util.release_interface(device, interface)