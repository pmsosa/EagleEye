from flask import *
import jsonpickle
from subprocess import Popen
from os import path
import requests
from IPython import embed
import cPickle as pickle
import random

from help import *


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
        self.timesteps = []
        self.version = int(random.random()*1000000000) ## Esentially used as a version number for the dataset. If there has been a modification then you change this number


TESTING = True #If set to true there will be no data collection just fake data
dataset = Dataset() ## Contains all the client packets and whatnot
#Not sure why I'm being forced to do this initialization....    
dataset.clients = []
dataset.monitor_info = []
dataset.mode = "init"
dataset.APs = []
dataset.timesteps = []

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

@app.route('/leaks/<client>')
def leaks(client):

    l = None;

    try:
        for c in dataset.clients:
            print c["mac"],client
            if (c["mac"] == client):
                print "found!"
                l = c["leak"]
    except:
        l = None;

    return render_template('leaks.html',client = client,leaks=l)

@app.route('/help/<item>')
def help(item):

    lines = None;

    if (item != "all"):
        try:
            lines = help_items[item];
        except:
            lines = None;

    return render_template('help.html',item=item,lines=lines,help_items=help_items)

##########################API CALLS#############################
# All API Calls                                                #
################################################################


#Returns the Dataset Structure
@app.route('/getalldataset')
def get_data():
    global dataset
    #if TESTING: data = dataset
    #else: data = jsonpickle.encode(dataset)
    data = jsonpickle.encode(dataset)
    resp = Response(response=data,status=200, mimetype="application/json")
    return resp

#Updates the Access Points
@app.route('/setPacketCaptr',methods=['POST'])
def add_Clients():
    global dataset
    content = request.get_json(silent=False)
    content = jsonpickle.encode(content)
    temp = jsonpickle.decode(content)
    dataset.clients = temp[0]
    dataset.timesteps = temp[1]
    dataset.version = int(random.random()*1000000000)
    return "OK"

#Updates the Clients Packet Capture
@app.route('/setAPs',methods=['POST'])
def add_APs():
    global dataset
    content = request.get_json(silent=False)
    content = jsonpickle.encode(content)
    dataset.APs = jsonpickle.decode(content)
    dataset.version = int(random.random()*1000000000)
    return "OK"

# User specifies WLAN name and password
@app.route('/start_monitor',methods=['POST'])
def setup():
    global dataset
    content = request.get_json(silent=False)
    content = jsonpickle.encode(content)
    temp = jsonpickle.decode(content)

    for ap in dataset.APs:
        if (ap["essid"]==temp["essid"]):
            dataset.monitor_info = {"essid":temp["essid"],"password":temp["password"],"mac":ap["mac"],"channel":ap["channel"]}
            break;

    dataset.mode = "mon"
    dataset.version = int(random.random()*1000000000)
    #You have to change setup.sh
    #proc = Popen(["sudo iwconfig wlan1 channel"+str(c)])
    #proc.wait();
    #proc =  Popen(["sudo ./dot11decrypt-master/build/dot11decrypt mon0 'wpa:"+dataset.monitor_info["essid"]+":"+dataset.monitor_info["password"]+"'"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
    #time.sleep(5);

    print "Moved wlan1 to channel",dataset.monitor_info["channel"]
    print "RUN:","sudo ./dot11decrypt-master/build/dot11decrypt mon0 'wpa:"+dataset.monitor_info["essid"]+":"+dataset.monitor_info["password"]+"'"
    proc2 = Popen(["sudo python packetCapture.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)    
    
    return "OK"


# Is server up or not?
@app.route('/alive',methods=['GET'])
def alive():
    print "Here be dragons..."
    return "Here be dragons.."

# Add a breakpoint. Useful for Debuggin'
@app.route('/break',methods=['GET'])
def breakpoint():
    global dataset, TESTING
    print "Entering Breakpoint"
    embed()
    return "OK"


if __name__ == "__main__":
    #Run setup.sh

    if (not TESTING):
        #proc = Popen(["sudo service avahi-daemon stop"])
        #proc.wait();
        #proc = Popen(["sudo service network-manager stop"])
        #proc.wait();
        #proc = Popen(["sudo airmon-ng start wlan1"])
        #proc.wait();
        #proc = Popen(["sudo python APFind.py])
        #proc.wait();
        

        proc = Popen(["sudo python APFind.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
        

        
        #proc = Popen(["sudo python packetCapture.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
    else:
        #proc = Popen(["sudo python APFind.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
        dataset.APs = [{"essid":"Fake AP#1","mac":"12:23:34:35","channel":6},{"essid":"Test AP","mac":"AF:22:44:55","channel":1}]
        #r = requests.post("http://localhost:1992/setAPs",headers={'Content-type':'application/json'},data=jsonpickle.encode(data))
        dataset.monitor_info = {"essid":"Konuko II","mac":"52:54:00:12:35:02","channel":"6","password":"vzla-mate"}
        dataset.mode = "mon"
        proc = Popen(["sudo python packetCapture.py fake"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
        
        # print "Loaded..."
        # output = open("data.pkl","rb")
        # dataset = pickle.load(output)
        # output.close()
        #embed()


    app.debug = True
    app.run(port=1992)

