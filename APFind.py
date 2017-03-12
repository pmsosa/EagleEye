###                    ###
# Access Point Discovery #
###                    ###

from scapy.all import *
import requests, jsonpickle
from IPython import embed

url = "http://localhost:1992"
endpoint = "setAPs"
iface = "mon0"
APs = []

#deb_pkts = []

### Record Access Point Packets
def rec_ap(packet):
    global APs
    try:
        #  type = Managment | subtype = Beacon
        if packet.type == 0 and packet.subtype == 8:
            name = packet[Dot11Elt].info
            if (name == ""): name = "<hidden>"
            element = {"essid":name,"mac":packet.addr2,"channel":int(ord(packet[Dot11Elt:3].info)),"pwr":-(256-ord(packet.notdecoded[-2:-1]))}
            for ap in APs:
                if (element["mac"] == ap["mac"]):
                    return None;


            print "Found:",packet.addr2,"("+packet[Dot11Elt].info+")","-C:",int(ord(packet[Dot11Elt:3].info))
            APs +=[element]

            #deb_pkts += [packet];

    except Exception, e:
        print "Error!",e
        return None

### Sniff Packets
def ap_find(timeout=10,iface="wlan0"):
    sniff(timeout=timeout,iface=iface,prn=rec_ap)


### Upload Data
def upload_data(url,data):
    r = requests.post(url,headers={'Content-type':'application/json'},data=jsonpickle.encode(data))

### Main Entry Point
if __name__ == "__main__":
    ap_find(3,iface)
    print APs
    try:
        upload_data(url+"/"+endpoint,APs)
    except:
        print "failed upload."
        pass;
    #embed();