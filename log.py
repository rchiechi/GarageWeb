# import os
import RPi.GPIO as GPIO
import os
import time
from datetime import datetime
import logging
from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
from util import getGarageDoorState
from util import lastDoorState
from util import LOGFILE

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('GarageWebLogger')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)
fileHandler = logging.FileHandler(LOGFILE)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

logger.info("Hello! Program Starting.")
print(" Control + C to exit Program")

TimeDoorOpened = datetime.strptime(
    datetime.strftime(datetime.now(),
                      '%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')  # Default Time
DoorOpenTimer = 0  # Default start status turns timer off
DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started

try:
    while True:
        if os.path.getsize(LOGFILE) > 1024**2:
            os.unlink(LOGFILE)  # Prune log file when it hits 1 MB
        logger.info("Last door state was: %s", lastDoorState())
        time.sleep(5)
        if DoorOpenTimer == 1:  # Door Open Timer has Started
            currentTimeDate = datetime.strptime(
                datetime.strftime(datetime.now(),
                                  '%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
            if (currentTimeDate - TimeDoorOpened).seconds > 900 and DoorOpenTimerMessageSent == 0:
                logger.info("Your Garage Door has been Open for 15 minutes")
                DoorOpenTimerMessageSent = 1

        if getGarageDoorState() == DOORUNKNOWN:  # Door Status is Unknown
            logger.info("Door Opening/Closing")
            while GPIO.input(16) == GPIO.HIGH and GPIO.input(18) == GPIO.HIGH:
                time.sleep(.5)
        else:
            if getGarageDoorState() == DOORCLOSED:  # Door is Closed
                logger.info("Door Closed")
                DoorOpenTimer = 0

            if getGarageDoorState() == DOOROPEN:  # Door is Open
                logger.info("Door Open")
                # Start Door Open Timer
                TimeDoorOpened = datetime.strptime(
                    datetime.strftime(datetime.now(),
                                      '%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                DoorOpenTimer = 1
                DoorOpenTimerMessageSent = 0

except KeyboardInterrupt:
    logger.info('Goodbye! -- Log Program Shutdown')
    GPIO.cleanup()
