from scapy.all import *

###Client Object ###
class Client:
    def __init__(self):
        self.mac = ""   # MAC
        self.ip = ""    # IP
        self.name = ""  # Gotten by Nmap Sweep
        self.os = ""    # Mac, Linux, Windows, Other, N/A
        self.usage = [] # Probably a list of dictionaries [{'timestamp':'9:00:00','https':'20%','udp':'80%'},...]

###Data Storage ###
class Dataset:
    def __init__(self):
        self.clients = ""
        self.aps = ""

def packet_callback(packet):
    print "Packet going to:", packet.dst

# Idea:
# dot11decrypt will throw to tapN interface, and scapy will read from tap0
# Scapy will then roughly parse through the packets and save the relevant info onto the dataset.
# We will have a few API calls hosted through a Flask server.
# The Client Frontend will call the API endpoints, recieve the preliminary info and then run some extra data analysis on its own. (That way we share the burden between server and client).
# Finally the data is presented using charts and other nice UI elements
p = sniff(timeout=3,prn=packet_callback,iface="tap0")   


