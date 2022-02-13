__all__ = [DOOROPEN, DOORCLOSED, DOORUNKNOWN, getGarageDoorState]
import os

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)  # the pin numbers refer to the board connector not the chip
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.IN, GPIO.PUD_UP)  # set up pin 16 as input and pull up to 3V via software pull-up resistor
GPIO.setup(18, GPIO.IN, GPIO.PUD_UP)  # set up pin 18 as input and pull up to 3V via software pull-up resistor
GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, GPIO.HIGH)
GPIO.setup(13, GPIO.OUT)
GPIO.output(13, GPIO.HIGH)
GPIO.setup(15, GPIO.OUT)
GPIO.output(15, GPIO.HIGH)


DOOROPEN = 1
DOORCLOSED = 0
DOORUNKNOWN = -1

def getPassword(fn = None):
    if fn is None: #  By default read from file "pw" in same dir as python scripts
        fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pw")  
    if not os.path.exists(fn):
        return "12345678"  #  If pw file does not exist, return default password
    with open(fn, 'rt') as fh:
        # Read first 128 bytes of file and return as a string
        return fh.read(128).strip()


def getGarageDoorState():
    if GPIO.input(16) == GPIO.LOW and GPIO.input(18) == GPIO.LOW:
        return DOORUNKNOWN
    else:
        if GPIO.input(16) == GPIO.HIGH:
            return DOORCLOSED
        if GPIO.input(18) == GPIO.HIGH:
            return DOOROPEN