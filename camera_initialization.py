from BosonSDK import *
import serial
import time

def initialize_camera():
    try:
        myCam = CamAPI.pyClient(manualport="/dev/ttyACM0")
        myCam.bosonRunFFC()
        time.sleep(3)
        return myCam
    except IOError:
        print("The camera is not connected")
        return None
