import time
import logging
from flask import Flask
from flask import request
from flask import redirect
from flask import jsonify
from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
# from util import door_dict
# from util import DOOROPENING
# from util import DOORCLOSING
from util import toggleGarageDoorState
from util import getGarageDoorState
from util import getPassword
from util import getLastDoorState
from util import recordDoorState
from util import triggerWebHook
from util import LOGFILE

logFormatter = logging.Formatter("%(name)s: %(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger('GarageWeb')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)
logger.setLevel(logging.DEBUG)

PASSWORD = getPassword()

app = Flask(__name__)


def getparam(param):
    """Get parameters of GET or POST request."""
    if request.method == 'POST':
        if param in request.form:
            return request.form[param]
    elif request.method == 'GET':
        if param in request.args:
            return request.args[param]
    return ""


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
    __pw = getparam('garagecode')
    __action = getparam('action')

    logger.debug("action: %s" % __action)

    if __pw == PASSWORD:  # Default password to open the door is 12345678 override using file pw
        # Trigger action webhook
        if triggerWebHook(__action):
            logger.debug("Webook triggered.")
        else:
            logger.debug('Webhook failed to trigger.')
        # Process a specific action request
        if __action == 'close' and getLastDoorState() == DOOROPEN:
            toggleGarageDoorState()
            recordDoorState(DOORCLOSED)
            return status()
        elif __action == 'open' and getLastDoorState() == DOORCLOSED:
            toggleGarageDoorState()
            recordDoorState(DOOROPEN)
            return status()
        elif __action:
            return status()

        toggleGarageDoorState()  # If no action is specified, just toggle the door

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
    return jsonify({'inputs': [{'input': __door_state}]})


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
