import time
import logging
from flask import Flask, request


# import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BOARD)  # the pin numbers refer to the board connector not the chip
# GPIO.setwarnings(False)
# GPIO.setup(16, GPIO.IN, GPIO.PUD_UP)  # set up pin 16 as input and pull up to 3V via software pull-up resistor
# GPIO.setup(18, GPIO.IN, GPIO.PUD_UP)  # set up pin 18 as input and pull up to 3V via software pull-up resistor
# GPIO.setup(7, GPIO.OUT)
# GPIO.output(7, GPIO.HIGH)
# GPIO.setup(11, GPIO.OUT)
# GPIO.output(11, GPIO.HIGH)
# GPIO.setup(13, GPIO.OUT)
# GPIO.output(13, GPIO.HIGH)
# GPIO.setup(15, GPIO.OUT)
# GPIO.output(15, GPIO.HIGH)

from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
from util import getGarageDoorState
from util import getPassword

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('GarageWeb')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)
# fileHandler = logging.FileHandler(LOGFILE)
# fileHandler.setFormatter(logFormatter)
# logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

PASSWORD = getPassword()()

app = Flask(__name__)

def handle_garage_status():  # User feedback about garage status
    if getGarageDoorState() == DOORUNKNOWN:
        logger.debug("Garage is Opening/Closing")
        return app.send_static_file('Question.html')
    else:
        if getGarageDoorState() == DOORCLOSED:
            logger.debug("Garage is Closed")
            return app.send_static_file('Closed.html')
        if getGarageDoorState() == DOOROPEN:
            logger.debug("Garage is Open")
            return app.send_static_file('Open.html')



@app.route('/', methods=['GET', 'POST'])
def index():
    return handle_garage_status()

@app.route('/garage', methods=['GET', 'POST'])
def Garage():
    name = request.form['garagecode']
    if name == PASSWORD:  # Default password to open the door is 12345678 override using file pw
        GPIO.output(7, GPIO.LOW)
        time.sleep(1)
        GPIO.output(7, GPIO.HIGH)
        time.sleep(2)
        return handle_garage_status()

    if name != PASSWORD:
        if name == "":
            name = "NULL"
        logger.debug("Garage Code Entered: " + name)
        return handle_garage_status()

@app.route('/stylesheet.css')
def stylesheet():
    return app.send_static_file('stylesheet.css')

@app.route('/log')
def logfile():
    return app.send_static_file('log.txt')

@app.route('/images/<picture>')
def images(picture):
    return app.send_static_file('images/' + picture)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
