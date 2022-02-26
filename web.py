import time
import logging
from flask import Flask
from flask import request
from flask import redirect
from flask import jsonify
from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
from util import door_dict
# from util import DOOROPENING
# from util import DOORCLOSING
from util import toggleGarageDoorState
from util import getGarageDoorState
from util import getPassword
from util import getLastDoorState
from util import recordDoorState
from util import LOGFILE

logFormatter = logging.Formatter("%(name)s: %(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('GarageWeb')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)
logger.setLevel(logging.DEBUG)

PASSWORD = getPassword()

app = Flask(__name__)

def update_saved_door_state():
    __door_state = getGarageDoorState()
    if __door_state in (DOOROPEN, DOORCLOSED):
        recordDoorState(__door_state)
    return __door_state

def handle_garage_status():  # User feedback about garage status
    __door_state = update_saved_door_state()
    if __door_state == DOORCLOSED:
        logger.debug("Garage is Closed")
        return app.send_static_file('Closed.html')
    if __door_state == DOOROPEN:
        logger.debug("Garage is Open")
        return app.send_static_file('Open.html')
    elif __door_state == DOORUNKNOWN:
        if getLastDoorState() == DOORCLOSED:
            logger.debug("Garage is Opening")
        elif getLastDoorState() == DOOROPEN:
            logger.debug("Garage door in Closing")
        else:
            logger.debug("Garage door is Opening/Closing")
        return app.send_static_file('Question.html')
    else:
        logger.error("Door is in impossible state!")
        return app.send_static_file('Question.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    return handle_garage_status()

@app.route('/garage', methods=['GET', 'POST'])
def Garage():
    if 'garagecode' in request.form:
        __pw = request.form['garagecode']
    elif 'garagecode' in request.args:
        __pw = request.args['garagecode']
    else:
        __pw = ""

    if __pw == PASSWORD:  # Default password to open the door is 12345678 override using file pw
        toggleGarageDoorState()
        if getLastDoorState() == DOORCLOSED:
            recordDoorState(DOOROPEN)
        elif getLastDoorState() == DOOROPEN:
            recordDoorState(DOORCLOSED)
        else:
            logger.debug("Found unknown door state sleeping for 5 and setting to current state.")
            time.sleep(5)
            recordDoorState(getGarageDoorState())
        if request.method == 'POST':  # TODO: figure out if request came from static html
            return redirect("/", code=302)
        else:
            return status()

    if __pw != PASSWORD:
        if __pw == "":
            __pw = "NULL"
        logger.debug("Last state: %s", getLastDoorState())
        logger.debug("Garage Code Entered: %s", __pw)
        return redirect("/", code=302)

@app.route('/status', methods=['GET', 'POST'])
def status():
    __door_state = update_saved_door_state()
    logger.debug("Status polled: %s.", __door_state)
    #  Return JSON path like Shelly1
    #  https://github.com/bydga/homebridge-garage-door-shelly1#readme
    return jsonify({'inputs': [{'input':__door_state}]})

@app.route('/stylesheet.css')
def stylesheet():
    return app.send_static_file('stylesheet.css')

@app.route('/log')
def logfile():
    return app.send_static_file(LOGFILE)

@app.route('/images/<picture>')
def images(picture):
    return app.send_static_file('images/' + picture)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
