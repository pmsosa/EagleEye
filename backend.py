from flask import *
from main import *
import jsonpickle
from subprocess import Popen
from os import path

app = Flask(__name__)




TESTING = False #If set to true there will be no data collection just fake data

dataset = Dataset()


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

@app.route('/getalldataset')
def get_data():
    global dataset
    data = jsonpickle.encode(dataset)
    resp = Response(response=data,status=200, mimetype="application/json")

    return resp

@app.route('/setdata',methods=['POST'])
def add_data():
    global dataset
    content = request.get_json(silent=False)
    print content
    content = jsonpickle.encode(content)
    dataset = jsonpickle.decode(content)
    return "OK"


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
        proc = Popen(["sudo python main.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)
    else:
        dataset = Dataset(debug=True)
        dataset.APs = ["AB:CD:EF","22:2D:3F","CC:33:FF"]
        dataset.clients_name = ["5B:EE:DF","52:2D:5F","C5:51:FD"]


    





    app.debug = True
    app.run(port=1992)

