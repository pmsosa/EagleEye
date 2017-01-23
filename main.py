from scapy.all import *
import time, copy, requests, jsonpickle

timestep = 5 # 5 Seconds (Equivalent to the granularity of the graphs)


### Client Object ###
class Client:

    windowsize = timestep
    template = {'timestamp': None, 'sent': 0,'recv': 0,'tcp': 0,'udp': 0,'http': 0,'https': 0}

    def __init__(self,mac,ip="",name="",os="",debug=False):
        self.last_timestamp = [time.time(),time.ctime()] # [Millisecs,Timestamp]
        self.mac = mac   # MAC
        self.ip = ""     # IP
        self.name = ""   # Gotten by Nmap Sweep
        self.os = ""     # Mac, Linux, Windows, Other, N/A
        self.report = [[self.last_timestamp[0],copy.deepcopy(self.template)]] # Probably a list of dictionaries [{'timestamp':'9:00:00','https':'20%','udp':'80%'},...]
        self.debug = debug

    def record_packet(self,packet):
        t = time.time()

        if (self.debug):
            print "-----------------------"
            print self.report
        

        if (t < self.last_timestamp[0] + self.windowsize):
            if self.debug: print ">> In Window!"
            #Packet is inside window size
            element = self.report[len(self.report)-1][1] #This is a shallow copy        
            
        else:
            self.last_timestamp = [time.time(),time.ctime()]
            if self.debug: print "<< Out of Window!"
            #Packet is outside of window size   
            element = copy.deepcopy(self.template)
            node = [self.last_timestamp[0], element]
            self.report += [node] #This is still a shallow appending

        # { 'timestamp': ,'sent':, 'recieved':,'http':,'udp':...}
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

### Data Storage ###
class Dataset:
    window = timestep
    
    def __init__(self,debug=False):
        self.clients = []
        self.APs = []
        self.clients_names = []
        self.debug = debug

    def sniff(self,timeout=None,iface="tap0"):
        sniff(timeout=timeout,iface=iface,prn=self.rec_packet)
    
    def os_fingerprint(self,src):
        print "TODO! Check the nmap fingerprint module to define clients"
        return None;
    
    def rec_ap(self,packet):
        try:
            #  type = Managment | subtype = Beacon
            if packet.type == 0 and packet.subtype == 8:
                if packet.addr2 not in self.APs:
                    if self.debug: print "Found:",packet.addr2,"("+packet[Dot11Elt].info+")","-C:",int(ord(packet[Dot11Elt:3].info))
                    self.APs +=[packet.addr2]

        except Exception, e:
            print "Error!",e
            return None

    def ap_find(self,timeout=10,iface="wlan0"):
        sniff(timeout=timeout,iface=iface,prn=self.rec_ap)

    def rec_packet(self,packet):
        try:

            # -------| Record Source |-------
            if packet.src not in self.clients_names:
                #Add client to our dataset if we haven't seen 'em before.           
                self.clients_names += [packet.src]
                self.clients += [Client(packet.src)]
            else:
                #Dangreous (but I don't want to do linear search each time)
                self.clients[self.clients_names.index(packet.src)].record_packet(packet)
                
                
            # -------| Record Destination |-------
            if packet.dst not in self.clients_names:
                #Add client to our dataset if we haven't seen 'em before.   
                self.clients_names += [packet.dst]
                self.clients += [Client(packet.dst)]
            else:
                #Dangreous (but I don't want to do linear search each time)
                self.clients[self.clients_names.index(packet.dst)].record_packet(packet)
        
                if (self.debug):
                    self.print_debuggin_info()

                #self.upload_data(self,"http://localhost:1993/setdata")

        except Exception, e:
                print "ERROR:",e
                print packet.show()

    def print_debuggin_info(self):
        print "---Clients:"
        for c in self.clients:
            print "  MAC:",c.mac
            print " ",c.report[len(c.report)-1]
            print " "

    def upload_data(self,url):
        r = requests.post(url,headers={'Content-type':'application/json'},data=jsonpickle.encode(self))



if __name__ == "__main__":
    dataset = Dataset(debug=True)
    dataset.ap_find(3,"mon0")
    dataset.upload_data("http://localhost:1993/setdata")
    print dataset.APs
    dataset.sniff(30,"tap0")

#def packet_callback(packet):
#    print "Packet going to:", packet.dst

# Idea:
# dot11decrypt will throw to tapN interface, and scapy will read from tap0
# Scapy will then roughly parse through the packets and save the relevant info onto the dataset.
# We will have a few API calls hosted through a Flask server.
# The Client Frontend will call the API endpoints, recieve the preliminary info and then run some extra data analysis on its own. (That way we share the burden between server and client).
# Finally the data is presented using charts and other nice UI elements
#p = sniff(timeout=3,prn=packet_callback,iface="tap0")   


