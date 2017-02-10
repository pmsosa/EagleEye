###                    ###
# Access Point Discovery #
###                    ###

from scapy.all import *
import requests, jsonpickle

url = "http://localhost:1992"
endpoint = "setAPs"
iface = "mon0"
APs = []

### Record Access Point Packets
def rec_ap(packet):
    global APs
    try:
        #  type = Managment | subtype = Beacon
        if packet.type == 0 and packet.subtype == 8:
            element = {"name":packet[Dot11Elt].info,"mac":packet.addr2,"channel":int(ord(packet[Dot11Elt:3].info))}
            if element not in APs:
                print "Found:",packet.addr2,"("+packet[Dot11Elt].info+")","-C:",int(ord(packet[Dot11Elt:3].info))
                APs +=[element]

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
    upload_data(url+"/"+endpoint,APs)
