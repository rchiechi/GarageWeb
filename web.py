import time
import logging
from flask import Flask
from flask import request
from flask import redirect
from flask import jsonify
from werkzeug.exceptions import BadRequestKeyError
from util import DOOROPEN
from util import DOORCLOSED
from util import DOORUNKNOWN
from util import DOOROPENING
from util import DOORCLOSING
from util import toggleGarageDoorState
from util import getGarageDoorState
from util import getPassword
from util import lastDoorState
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
        if lastDoorState() == DOORCLOSED:
            logger.debug("Garage is Opening")
        elif lastDoorState() == DOOROPEN:
            logger.debug("Garage door in Closing")
        else:
            logger.debug("Garage door is Opening/Closing")
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
    if 'garagecode' in request.form:
        name = request.form['garagecode']
    elif 'garagecode' in request.args:
        name = request.args['garagecode']
    else:
        name = ""

    if name == PASSWORD:  # Default password to open the door is 12345678 override using file pw
        toggleGarageDoorState()
        if lastDoorState() == DOORCLOSED:
            lastDoorState(DOOROPEN)
        elif lastDoorState() == DOOROPEN:
            lastDoorState(DOORCLOSED)
        else:
            logger.debug("Found unknown door state sleeping for 5 and setting to current state.")
            time.sleep(5)
            lastDoorState(getGarageDoorState())
        if request.method == 'POST': #  TODO: figure out if request came from static html
            return redirect("/", code=302)
        else:
            return status()
        #return handle_garage_status()

    if name != PASSWORD:
        if name == "":
            name = "NULL"
        logger.debug("Garage Code Entered: %s", name)
        return redirect("/", code=302)
        #return handle_garage_status()

@app.route('/status', methods=['GET', 'POST'])
def status():
    #  Return JSON path like Shelly1
    #  https://github.com/bydga/homebridge-garage-door-shelly1#readme
    return jsonify({'inputs': [{'input':getGarageDoorState()}]})

@app.route('/stylesheet.css')
def stylesheet():
    return app.send_static_file('stylesheet.css')

@app.route('/log')
def logfile():
    return app.send_static_file(LOGFILE)

@app.route('/images/<picture>')
def images(picture):
    logger.debug("Status polled.")
    return app.send_static_file('images/' + picture)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
