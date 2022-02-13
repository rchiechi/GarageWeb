# import os
import RPi.GPIO as GPIO
import time
from datetime import datetime
import logging
from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
from util import getGarageDoorState

LOGFILE = "/tmp/GarageWeb.log"

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('GarageWebLogger')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)
fileHandler = logging.FileHandler(LOGFILE)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)



#def emit_log(msg, preamble=''):
#    logfile = open(LOGFILE,"a")
#    __datetime = datetime.now().strftime("%s%Y/%m/%d -- %H:%M")
#    logfile.write("%s%s -- %s\n" % (preamble, __datetime, msg))
#    logfile.close()
#    print("%s%s -- %s\n" % (preamble, __datetime, msg))


logger.info("Hello! Program Starting.")
print(" Control + C to exit Program")

# GPIO.setmode(GPIO.BOARD)
# GPIO.setwarnings(False)

# GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# time.sleep(1)

TimeDoorOpened = datetime.strptime(
    datetime.strftime(datetime.now(),
                      '%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')  # Default Time
DoorOpenTimer = 0  # Default start status turns timer off
DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started

try:
    while True:
        time.sleep(1)
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
    logger.info('Goodbye!', '    Log Program Shutdown --  ')
    GPIO.cleanup()
