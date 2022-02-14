import os
import time
import RPi.GPIO as GPIO
import logging

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

LOGFILE = "/var/log/garageweb/GarageWeb.log"
STATEFILE = "/var/run/garageweb/garagedoor.state"
DOOROPEN = 0
DOORCLOSED = 1
DOOROPENING = 2
DOORCLOSING = 3
DOORUNKNOWN = -1

door_dict = {DOOROPEN: "Open",
             DOORCLOSED: "Closed",
             DOOROPENING: "Opening",
             DOORCLOSING: "Closing",
             DOORUNKNOWN: "Unknown"}

logFormatter = logging.Formatter("%(name)s: %(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('GarageWebUtil')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)
fileHandler = logging.FileHandler(LOGFILE)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

def getPassword(fn=None):
    if fn is None:  # By default read from file "pw" in same dir as python scripts
        fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pw")
    if not os.path.exists(fn):
        return "12345678"  # If pw file does not exist, return default password
    with open(fn, 'rt') as fh:
        # Read first 128 bytes of file and return as a string
        return fh.read(128).strip()


def getGarageDoorState():
    logger.debug("getGarageDoorState: Last door state was %s", door_dict[lastDoorState()])
    if GPIO.input(16) == GPIO.LOW and GPIO.input(18) == GPIO.LOW:
        if lastDoorState() == DOORCLOSED:
            logger.debug("getGarageDoorState: %s", door_dict[DOORCLOSED])
            return DOOROPENING
        elif lastDoorState() == DOOROPEN:
            logger.debug("getGarageDoorState: %s", door_dict[DOORCLOSING])
            return DOORCLOSING
        else:
            logger.debug("getGarageDoorState: %s", door_dict[DOORUNKNOWN])
            return DOORUNKNOWN
    else:
        if GPIO.input(16) == GPIO.HIGH:
            logger.debug("getGarageDoorState: %s", door_dict[DOORCLOSED])
            return DOORCLOSED
        if GPIO.input(18) == GPIO.HIGH:
            logger.debug("getGarageDoorState: %s", door_dict[DOOROPEN])
            return DOOROPEN

def toggleGarageDoorState():
    GPIO.output(7, GPIO.LOW)
    time.sleep(1)
    GPIO.output(7, GPIO.HIGH)
    __start = time.time()
    while getGarageDoorState() == DOORUNKNOWN:
        time.sleep(1)
        logger.debug("toggleGarageDoorState: Sleeping while door changed state.")
        if time.time() - __start > 30:
            break

def lastDoorState(set_state=None):
    if not os.path.exists(STATEFILE):
        set_state = -1
    if set_state is not None:
        set_state = int(set_state)
        logger.debug("lastDoorState: Setting door state %s", door_dict[set_state])
        with open(STATEFILE, 'wt') as fh:
            logger.debug("Writing %s to %s", set_state, STATEFILE)
            fh.write(str(set_state).strip())
        return set_state
    with open(STATEFILE, 'rt') as fh:
        return int(fh.read(128).strip())
