# import RPi.GPIO as GPIO  # type: ignore
import os
import time
from datetime import datetime
import logging
from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
# from util import DOOROPENING
# from util import DOORCLOSING
from util import getGarageDoorState
from util import triggerWebHook
from util import lastDoorState
from util import door_dict
from util import LOGFILE

logFormatter = logging.Formatter("%(name)s: %(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('GarageWebLogger')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)
fileHandler = logging.FileHandler(LOGFILE)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

logger.info("Hello! Program Starting.")
print(" Control + C to exit Program")


def gettimestring():
    __strftime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    return datetime.strptime(__strftime, '%Y-%m-%d %H:%M:%S')


TimeDoorOpened = gettimestring()  # Default Time
DoorOpenTimer = 0  # Default start status turns timer off
DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started

# try:
while True:
    if os.path.getsize(LOGFILE) > 1024**2:
        os.unlink(LOGFILE)  # Prune log file when it hits 1 MB
    logger.debug("Last door state was: %s", door_dict[lastDoorState()])
    time.sleep(10)
    if DoorOpenTimer == 1:  # Door Open Timer has Started
        currentTimeDate = gettimestring()
        if (currentTimeDate - TimeDoorOpened).seconds > 900 and DoorOpenTimerMessageSent == 0:
            logger.info("Your Garage Door has been Open for 15 minutes")
            DoorOpenTimerMessageSent = 1

    if getGarageDoorState() == DOORUNKNOWN:  # Door Status is Unknown
        logger.info("Door Opening/Closing")
        continue

    if getGarageDoorState() == DOORCLOSED:  # Door is Closed
        logger.info("Door Closed")
        DoorOpenTimer = 0
        triggerWebHook('update', 'closed')
        continue

    if getGarageDoorState() == DOOROPEN:  # Door is Open
        logger.info("Door Open")
        # Start Door Open Timer
        TimeDoorOpened = gettimestring()
        DoorOpenTimer = 1
        DoorOpenTimerMessageSent = 0
        triggerWebHook('update', 'open')
        continue

# except KeyboardInterrupt:
#    logger.info('Goodbye! -- Log Program Shutdown')
#    GPIO.cleanup()
