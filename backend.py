from flask import *
from main import *
import jsonpickle
from subprocess import Popen

app = Flask(__name__)


dataset = Dataset()

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

    proc = Popen(["sudo python main.py"],shell=True,stdin=None,stdout=None,stderr=None,close_fds=True)

    app.debug = True
    app.run(port=1993)

