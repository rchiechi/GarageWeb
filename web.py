import time
import logging
from flask import Flask, request
from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
from util import toggleGarageDoorState
from util import getGarageDoorState
from util import getPassword
from util import LOGFILE

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('GarageWeb')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)
logger.setLevel(logging.DEBUG)

PASSWORD = getPassword()

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
        toggleGarageDoorState()
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
    return app.send_static_file(LOGFILE)

@app.route('/images/<picture>')
def images(picture):
    return app.send_static_file('images/' + picture)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
