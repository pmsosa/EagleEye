from flask import *
from main import *
import jsonpickle
from subprocess import Popen
from os import path

app = Flask(__name__)


###            ###
# Dataset Object #
###            ###
class Dataset:
    def __init_():
        self.clients = []
        self.APs = []
        self.mode = "init"  ## Mode determines what the Front-End application is currently doing. (For if the user refreshes the page.)
                            ## "init" = Application just started. We need to look for access points and user has to stipulate which AP they want to monitor.
                            ## "mon"  = We are actively monitoring an AP



TESTING = False #If set to true there will be no data collection just fake data
dataset = Dataset() ## Contains all the client packets and whatnot    


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

# User specifies WLAN name and password
@app.route('/setup/<SSID>/<PASS>',methods=['GET'])
def setup(SSID,PASS):
    #TODO
    return 0


# Is server up or not?
@app.route('/alive',methods=['GET'])
def alive():
    print "Here be dragons..."
    return "Here be dragons.."


if __name__ == "__main__":

    # dataset = Dataset(debug=True)
    # dataset.ap_find(5,"mon0")
    # print dataset.APs
    # dataset.sniff(10,"tap0")

    if (not TESTING):
        proc = Popen(["sudo python APFind.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
        proc = Popen(["sudo python packetCapture.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
    else:

        dataset = Dataset(debug=True)
        dataset = '{"debug": true, "APs": ["60:e3:27:ac:58:f4", "54:3d:37:29:29:08", "54:3d:37:69:29:08", "54:3d:37:69:54:f8", "10:da:43:10:1f:b2", "00:30:44:1e:35:0f", "20:e5:2a:fa:85:b0", "20:e5:2a:22:7f:b6", "10:0d:7f:e2:5b:1d", "54:3d:37:29:54:f8", "54:3d:37:28:6f:28", "54:3d:37:68:6f:28", "20:e5:2a:fa:8f:e8", "9c:b6:54:fa:d5:59"], "clients": [{"name": "", "ip": "", "report": [[1486425825.977732, {"udp": 104, "http": 1, "timestamp": null, "tcp": 749, "https": 444, "recv": 496, "sent": 357}], [1486425843.680756, {"udp": 33, "http": 0, "timestamp": null, "tcp": 22, "https": 22, "recv": 26, "sent": 29}]], "mac": "b4:ae:2b:c9:41:30", "debug": false, "os": ""}, {"name": "", "ip": "", "report": [[1486425825.977732, {"udp": 4, "http": 0, "timestamp": null, "tcp": 0, "https": 0, "recv": 4, "sent": 0}]], "mac": "01:00:5e:7f:ff:fa", "debug": false, "os": ""}, {"name": "", "ip": "", "report": [[1486425825.977732, {"udp": 56, "http": 0, "timestamp": null, "tcp": 1, "https": 0, "recv": 39, "sent": 18}], [1486425831.646966, {"udp": 40, "http": 0, "timestamp": null, "tcp": 745, "https": 451, "recv": 313, "sent": 472}], [1486425838.486037, {"udp": 196, "http": 1, "timestamp": null, "tcp": 5434, "https": 3556, "recv": 2012, "sent": 3618}], [1486425858.877793, {"udp": 1, "http": 0, "timestamp": null, "tcp": 66, "https": 40, "recv": 27, "sent": 40}]], "mac": "60:e3:27:ac:58:f4", "debug": false, "os": ""}, {"name": "", "ip": "", "report": [[1486425825.977732, {"udp": 44, "http": 0, "timestamp": null, "tcp": 2580, "https": 1650, "recv": 1669, "sent": 959}], [1486425848.705005, {"udp": 88, "http": 1, "timestamp": null, "tcp": 1406, "https": 915, "recv": 941, "sent": 553}], [1486425853.705691, {"udp": 38, "http": 0, "timestamp": null, "tcp": 1488, "https": 1016, "recv": 1016, "sent": 510}]], "mac": "88:79:7e:46:2b:55", "debug": false, "os": ""}, {"name": "", "ip": "", "report": [[1486425831.646966, {"udp": 7, "http": 0, "timestamp": null, "tcp": 0, "https": 0, "recv": 7, "sent": 0}]], "mac": "01:00:5e:00:00:fb", "debug": false, "os": ""}, {"name": "", "ip": "", "report": [[1486425838.486037, {"udp": 0, "http": 0, "timestamp": null, "tcp": 0, "https": 0, "recv": 0, "sent": 0}]], "mac": "ff:ff:ff:ff:ff:ff", "debug": false, "os": ""}], "clients_names": ["b4:ae:2b:c9:41:30", "01:00:5e:7f:ff:fa", "60:e3:27:ac:58:f4", "88:79:7e:46:2b:55", "01:00:5e:00:00:fb", "ff:ff:ff:ff:ff:ff"]}'
        dataset = '{"py/object": "__main__.Dataset", "APs": [{"mac": "9c:b6:54:fa:d5:59", "name": "HP-Print-59-Photosmart 7520", "channel": 11}, {"mac": "00:30:44:1e:35:0f", "name": "CradlepointLP", "channel": 11}, {"mac": "dc:fe:07:c6:a7:80", "name": "EMPIRE IKES BACK", "channel": 11}, {"mac": "de:fe:07:c6:a7:86", "name": "CoxWiFi", "channel": 11}, {"mac": "60:e3:27:ac:58:f4", "name": "BlueMix", "channel": 11}, {"mac": "54:3d:37:29:29:08", "name": "ICON-MGMT", "channel": 11}, {"mac": "54:3d:37:69:29:08", "name": "ICON", "channel": 11}, {"mac": "54:3d:37:28:6f:28", "name": "ICON-MGMT", "channel": 11}, {"mac": "54:3d:37:68:6f:28", "name": "ICON", "channel": 11}, {"mac": "20:e5:2a:fa:8f:e8", "name": "FA8FE8", "channel": 11}, {"mac": "20:e5:2a:fa:8a:45", "name": "FA8A45", "channel": 11}, {"mac": "20:e5:2a:fa:85:b5", "name": "FA85B5", "channel": 11}, {"mac": "54:3d:37:28:6e:d8", "name": "ICON-MGMT", "channel": 6}], "clients": [{"name": "", "ip": "", "report": [[1486709743.292464, {"udp": 0, "http": 0, "tcp": 0, "https": 0, "recv": 0, "sent": 0}], [1486709750.503525, {"udp": 23, "http": 0, "tcp": 231, "https": 0, "recv": 0, "sent": 257}], [1486709757.344866, {"udp": 3, "http": 0, "tcp": 392, "https": 0, "recv": 0, "sent": 396}], [1486709762.36146, {"udp": 2, "http": 0, "tcp": 376, "https": 0, "recv": 0, "sent": 378}], [1486709767.366592, {"udp": 1, "http": 0, "tcp": 44, "https": 0, "recv": 0, "sent": 46}]], "mac": "88:79:7e:46:2b:55", "debug": false, "os": ""}, {"name": "", "ip": "", "report": [[1486709743.292464, {"udp": 10, "http": 0, "tcp": 0, "https": 0, "recv": 10, "sent": 0}]], "mac": "01:00:5e:00:00:fb", "debug": false, "os": ""}, {"name": "", "ip": "", "report": [[1486709750.503525, {"udp": 19, "http": 0, "tcp": 1042, "https": 0, "recv": 1061, "sent": 0}]], "mac": "60:e3:27:ac:58:f4", "debug": false, "os": ""}]}'

    





    app.debug = True
    app.run(port=1992)

