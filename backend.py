from flask import *
#from main import *
import jsonpickle
from subprocess import Popen
from os import path


app = Flask(__name__)


###            ###
# Dataset Object #
###            ###
class Dataset:
    def __init_():
        self.clients = None
        self.APs = None
        self.mode = "init"  ## Mode determines what the Front-End application is currently doing. (For if the user refreshes the page.)
                            ## "init" = Application just started. We need to look for access points and user has to stipulate which AP they want to monitor.
                            ## "mon"  = We are actively monitoring an AP
        self.monitor_info = None ## Monitor Info is a tuple: [Selected AP, Password]


TESTING = False #If set to true there will be no data collection just fake data
dataset = Dataset() ## Contains all the client packets and whatnot    
dataset.clients = []
dataset.monitor_info = []
dataset.mode = "init"
dataset.APs = []

#########################SERVING STATIC FILES###################
# Serving Static Files (THIS IS DANGREOUS)                     #
################################################################

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('client/css', path)

@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('client/fonts', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('client/img', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('client/js', path)

#########################TEMPLATE SITE##########################
# Redirects to actual HTML Sites                               #
################################################################

@app.route('/')
def home():
    return render_template('index.html')

##########################API CALLS#############################
# All API Calls                                                #
################################################################


#Returns the Dataset Structure
@app.route('/getalldataset')
def get_data():
    global dataset
    if TESTING: data = dataset
    else: data = jsonpickle.encode(dataset)
    resp = Response(response=data,status=200, mimetype="application/json")
    return resp

#Updates the Access Points
@app.route('/setPacketCaptr',methods=['POST'])
def add_Clients():
    global dataset
    content = request.get_json(silent=False)
    content = jsonpickle.encode(content)
    dataset.clients = jsonpickle.decode(content)
    return "OK"

#Updates the Clients Packet Capture
@app.route('/setAPs',methods=['POST'])
def add_APs():
    global dataset
    content = request.get_json(silent=False)
    content = jsonpickle.encode(content)
    dataset.APs = jsonpickle.decode(content)
    return "OK"

# User specifies WLAN name and password
@app.route('/start_monitor',methods=['POST'])
def setup():
    global dataset
    content = request.get_json(silent=False)
    content = jsonpickle.encode(content)
    dataset.monitor_info = jsonpickle.decode(content)
    dataset.mode = "mon"
    #You have to change setup.sh
    #proc1 =  Popen(["sudo ./dot11decrypt-master/build/dot11decrypt mon0 'wpa:"+dataset.monitor_info["bssid"]+":"+dataset.monitor_info["password"]+"'"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
    print "RUN:","sudo ./dot11decrypt-master/build/dot11decrypt mon0 'wpa:"+dataset.monitor_info["bssid"]+":"+dataset.monitor_info["password"]+"'"
    proc2 = Popen(["sudo python packetCapture.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)    
    
    return "OK"


# Is server up or not?
@app.route('/alive',methods=['GET'])
def alive():
    print "Here be dragons..."
    return "Here be dragons.."

#DEPRECATED (Divided into /setAPs and /setPacketCaptr)
# # Updates the Dataset Structure
# @app.route('/setdata',methods=['POST'])
# def add_data():
#     global dataset
#     content = request.get_json(silent=False)
#     print content
#     content = jsonpickle.encode(content)
#     dataset = jsonpickle.decode(content)
#     return "OK"

if __name__ == "__main__":
    global dataset
    #Run setup.sh

    if (not TESTING):
        proc = Popen(["sudo python APFind.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
        #proc = Popen(["sudo python packetCapture.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)



    app.debug = True
    app.run(port=1992)

