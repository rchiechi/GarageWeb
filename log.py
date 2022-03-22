import os
import time
import logging
from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
from util import LOGFILE
from util import getGarageDoorState
from util import triggerWebHook
from util import getLastDoorState
from util import door_dict

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

TimeDoorOpened = time.time()  # Default Time
DoorOpenTimer = 0  # Default start status turns timer off
DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started


while True:
    try:
        if os.path.getsize(LOGFILE) > 1024**2:
            os.unlink(LOGFILE)  # Prune log file when it hits 1 MB
    except FileNotFoundError:
        pass  # Don't crash if the file does not exist
    logger.debug("Last door state was: %s", door_dict[getLastDoorState()])
    time.sleep(10)
    if DoorOpenTimer == 1:  # Door Open Timer has Started
        if time.time() - TimeDoorOpened > 900 and DoorOpenTimerMessageSent == 0:
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
        TimeDoorOpened = time.time()
        DoorOpenTimer = 1
        DoorOpenTimerMessageSent = 0
        triggerWebHook('update', 'open')
        continue
