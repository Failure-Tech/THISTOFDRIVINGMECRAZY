import can
import time

START = 0x08
STOP = 0x09
QUERY = 0x1C


class TOF:
    
    def __init__(self, port, br = 1000000):

        self.bitrate = br
        self.port = port

        self.interface = can.interface.Bus(interface = 'slcan', channel = port, bitrate = self.bitrate)


    def startMeasurements(self):
        
        message = can.Message(arbitration_id = START, is_remote_frame = True, dlc = 0, is_extended_id = False)
        
        try:

            self.interface.send(message)
            print(f"Start message '{START}' sent on {self.port}")

        except can.CanError:

            print("Start message NOT sent.")


    def stopMeasurements(self):
        
        message = can.Message(arbitration_id = STOP, is_remote_frame = True, dlc = 0, is_extended_id = False)
        
        try:

            self.interface.send(message)
            print(f"Stop message '{STOP}' sent on {self.port}")

        except can.CanError:

            print("Stop message NOT sent.")


    def collectMeasurments():
        
        # TODO

        pass


sensor = TOF(port = 'COM6')

sensor.startMeasurements()
time.sleep(2)
sensor.stopMeasurements()


sensor.interface.shutdown()