import can
import time

START = 0x08
STOP = 0x09
QUERY = 0x1C


class TOF:
    
    def __init__(self, port, br = 1000000):

        self.bitrate = br
        self.port = port

        self.filter = [
            {"can_id": 0x1C, "can_mask": None, "extended": False},
            {"can_id": 0x08, "can_mask": None, "extended": False},
            {"can_id": 0x09, "can_mask": None, "extended": False}
        ]

        self.interface = can.interface.Bus(interface = 'slcan', channel = port, 
                                           bitrate = self.bitrate)


    def startMeasurements(self):
        
        message = can.Message(arbitration_id = START, is_remote_frame = True, dlc = 0, is_extended_id = False)
        
        try:

            self.interface.send(message)
            print(f"Start message '{START}' sent on {self.port}")

        except can.CanError:
            
            self.interface.shutdown()
            print("Start message NOT sent.")


    def stopMeasurements(self):
        
        message = can.Message(arbitration_id = STOP, is_remote_frame = True, dlc = 0, is_extended_id = False)
        
        try:

            self.interface.send(message)
            print(f"Stop message '{STOP}' sent on {self.port}")

        except can.CanError:
            
            self.interface.shutdown()
            print("Stop message NOT sent.")

    def collectMeasurements(self):
        
        # Add UTC time to data output

        response = self.interface.recv(timeout = 2)

        data = response.data

        if response == None:
        
            print("Data not recieved.")

        else:
            # print("dlc:", response.dlc)
            # print("RAW: " + str(data))
            self.interpretMeasurements(data)

    def interpretMeasurements(self, meas):

        dataDictionary = {}
        
        distance = (meas[0] << 16) + (meas[1] << 8) + meas[2]

        # converts the distance from Q9.14
        distance = distance / 16384.0

        dataDictionary["distance"] = distance 

        amplitude = (meas[3] << 8) + meas[4]
        
        # converys the amplitude from UQ12.4
        amplitude = amplitude / 16.0

        dataDictionary["amplitude"] = amplitude 

        signalQuality = meas[5]

        dataDictionary["signalQuality"] = signalQuality

        status = (meas[6] << 8) + meas[7]
        
        # converts status from 16-bit unsigned int to 16-bit signed int
        if not status < 0x8000:

            status = status - 0x10000

        dataDictionary["distance"] = distance 

        return dataDictionary

sensor = TOF(port = 'COM6')

try:

    sensor.startMeasurements()

    for i in range(100):
        
        try: 

            data = sensor.collectMeasurements()

        except:
            
            sensor.interface.shutdown()

        # print(f"distance: {data.distance}, amplitude: {data.amplitude}, signal quality: {data.signalQuality}, status: {data.status}", end = "\r")

        print(data)

        time.sleep(0.2)

    print("")

    time.sleep(2)
    sensor.stopMeasurements()

    sensor.interface.shutdown()

except KeyboardInterrupt:

    sensor.stopMeasurements()
    sensor.interface.shutdown()
    time.sleep(0.1)