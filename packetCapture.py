from scapy.all import *
import time, copy, requests, jsonpickle
import sys
from IPython import embed

url = "http://localhost:1992"
endpoint = "setPacketCaptr"
iface = "tap0"
timeout = 120 # For unlimited time set = None

timestep = 5 # 5 Seconds (Equivalent to the granularity of the graphs)
clients = []
clients_names = []
debug = False



### Client Object ###
class Client:

    windowsize = timestep
    timesteps = [time.time()]; #List of shared timesteps done by all points.
    
    template = {'sent': 0,'recv': 0,'tcp': 0,'udp': 0,'http': 0,'https': 0}
    #template = {'timestamp': None, 'sent': 0,'recv': 0,'tcp': 0,'udp': 0,'type':{}}
    # Timewindow must be "static" among clients so the points on the graph match nicely.
    #last_timestamp = [time.time(),time.ctime()] # [Millisecs,Timestamp]

    def __init__(self,mac,ip="",name="",os="",debug=False):
        if (Client.timesteps == []): Client.timesteps = [time.time()];
        self.mac = mac   # MAC
        self.ip = ip     # IP
        self.name = name   # Gotten by Nmap Sweep
        self.os = os     # Mac, Linux, Windows, Other, N/A
        self.report = [[Client.timesteps[-1],copy.deepcopy(self.template)]] # Probably a list of dictionaries [{'timestamp':'9:00:00','https':'20%','udp':'80%'},...]
        self.debug = debug

    def record_packet(self,packet):
        t = time.time()

        if (self.debug):
            print "-----------------------"
            print self.report
        

        if (t < Client.timesteps[-1] + self.windowsize):
            if self.debug: print ">> In Window!"
            #Packet is inside window size
            element = self.report[len(self.report)-1][1] #This is a shallow copy        
            
        else:
            Client.timesteps += [time.time()]
            if self.debug: print "<< Out of Window!"
            #Packet is outside of window size   
            element = copy.deepcopy(self.template)
            node = [Client.timesteps[-1], element]
            self.report += [node] #This is still a shallow appending

        # { 'timestamp': ,'sent':, 'recieved':,'type':['80':'443':...etc.]}
        if self.debug:
            print element
            print "-----------------------"

        #Sent or Recieved
        if (packet.dst == self.mac): element["recv"] +=1
        elif (packet.src == self.mac): element["sent"] +=1

        #Transport Layer (UDP, TCP)
        if (packet.proto == 6): element["tcp"] +=1
        elif (packet.proto == 17): element["udp"] +=1
        
        #Application Layer (HTTP, HTTPS)
        if (packet.sport == 443): element["https"] += 1
        elif (packet.sport == 80): element["http"] = 1

        #Keep packets in dict type
        #try:
            #If this crashes then entry for this port doesn't exist, so we must create it.
        #    element["type"][str(packet.sport)] += 1
        #except:
        #    element["type"][str(packet.sport)] = 1

        ### Constraint Size of Report to 1000 datapoints ~ 5000s (1.3 hours) = ###
        if (len(self.report) > 1000):
            self.report = self.report[1:]


### Data Storage ###
def monitor(timeout=None,iface="tap0"):
    if timeout==None:
        sniff(iface=iface,prn=rec_packet)
    else:
        sniff(timeout=timeout,iface=iface,prn=rec_packet)
        
    
def rec_packet(packet):
    global clients_names,clients,debug
    try:
        t = time.time()        
        ## --- Should we send an Update to Flask Server--- ##
        if (t > Client.timesteps[-1] + timestep):
            upload_data()


        # -------| Record Source |-------
        if packet.src not in clients_names:
            #Add client to our dataset if we haven't seen 'em before.           
            clients_names += [packet.src]
            clients += [Client(packet.src,packet.getlayer(IP).src,packet.src,"Unknown")]
        else:
            #Dangreous (but I don't want to do linear search each time)
            clients[clients_names.index(packet.src)].record_packet(packet)
            
            
        # -------| Record Destination |-------
        if packet.dst not in clients_names:
            #Add client to our dataset if we haven't seen 'em before.   
            clients_names += [packet.dst]
            clients += [Client(packet.dst,packet.getlayer(IP).src,packet.src,"Unknown")]
        else:
            #Dangreous (but I don't want to do linear search each time)
            clients[clients_names.index(packet.dst)].record_packet(packet)
    
            if (debug):
                print_debuggin_info()



    except Exception, e:
            print "ERROR:",e
            #print packet.show()

def print_debuggin_info():
    global clients
    print "---Clients:"
    for c in clients:
        print "  MAC:",c.mac
        print " ",c.report[len(c.report)-1]
        print " "

def upload_data():
    global clients,url,endpoint
    try:
        temp = [clients,clients[0].timesteps]
        print temp
        r = requests.post(url+"/"+endpoint,headers={'Content-type':'application/json'},data=jsonpickle.encode(temp))
    except:
        print "Failed to Upload Data"


if __name__ == "__main__":
    monitor(timeout,iface)
    #embed()