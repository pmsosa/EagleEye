from scapy.all import *
import time, copy, requests, jsonpickle
import sys
from IPython import embed
import traceback

url = "http://localhost:1992"
endpoint = "setPacketCaptr"
iface = "tap0"
timeout = 120 # For unlimited time set = None

timestep = 5 # 5 Seconds (Equivalent to the granularity of the graphs)
clients = []
clients_names = []
aks = {}
debug = False



### Client Object ###
class Client:

    windowsize = timestep
    timesteps = [] #[time.time()]; #List of shared timesteps done by all points.
    
    #template = {'sent': 0,'recv': 0,'tcp': 0,'udp': 0,'http': 0,'https': 0}
    template = {'sent': 0,'recv': 0,'tcp': 0,'udp': 0,'ports': {}, 'upsize': 0, 'downsize' : 0, "downdrops":0, "updrops":0}
    #template = {'timestamp': None, 'sent': 0,'recv': 0,'tcp': 0,'udp': 0,'type':{}}
    # Timewindow must be "static" among clients so the points on the graph match nicely.
    #last_timestamp = [time.time(),time.ctime()] # [Millisecs,Timestamp]

    def __init__(self,mac,ip="",name="",os="",debug=False):
        #if (Client.timesteps == []): Client.timesteps = [time.time()];
        #aks.update({mac:[[],[]]}) # {MAC,[[SENT ACKS, RECV ACKS], [SENT ACKS, RECV ACKS]]}
        aks.update({mac:{"sent":[[],[]],"recv":[[],[]]}})
        self.mac = mac   # MAC
        self.ip = ip     # IP
        self.name = name # Gotten by Nmap Sweep
        self.os = os     # Mac, Linux, Windows, Other, N/A
        self.report = [[Client.timesteps[-1],copy.deepcopy(self.template)]] # Probably a list of dictionaries [{'timestamp':'9:00:00','https':'20%','udp':'80%'},...]
        self.leak = [];
        self.debug = debug

    def record_packet(self,packet):
        #print ".",
        t = packet.time #t = packet.payload.time #t = time.time()
        
        if (self.debug):
            print "-----------------------"
            print self.report
        

        if (t < Client.timesteps[-1] + self.windowsize):
            if self.debug: print ">> In Window!"
            #Packet is inside window size
            element = self.report[len(self.report)-1][1] #This is a shallow copy        
            
        else:
            new_timestep = t - (t - Client.timesteps[0])%timestep
            Client.timesteps += [new_timestep] #[time.time()]
            if self.debug: print "<< Out of Window!"
            #Packet is outside of window size   
            element = copy.deepcopy(self.template)
            node = [Client.timesteps[-1], element]
            self.report += [node] #This is still a shallow appending
            aks[self.mac]["sent"][0] = aks[self.mac]["sent"][1]
            aks[self.mac]["recv"][0] = aks[self.mac]["recv"][1]
            aks[self.mac]["sent"][1] = [] #Throw away all old acks
            aks[self.mac]["recv"][1] = [] #Throw away all old acks

        # { 'timestamp': ,'sent':, 'recieved':,'type':['80':'443':...etc.]}
        if self.debug:
            print element
            print "-----------------------"

        #Sent or Recieved
        if (packet.dst == self.mac): 
            element["recv"] +=1
            element["downsize"] += len(packet)*8   # In Bits
            try:
                if (packet.seq in aks[self.mac]["recv"][0] or packet.seq in aks[self.mac]["recv"][1]):
                    element["downdrops"] += 1
                else:
                    aks[self.mac]["recv"][1] += [packet.seq];
            except Exception, e:
                #print "r",e
                pass;

        elif (packet.src == self.mac): 
            element["sent"] +=1
            element["upsize"] += len(packet)*8 # In Bits
            try:
                if (packet.seq in aks[self.mac]["sent"][0] or packet.seq in aks[self.mac]["sent"][1]):
                    element["updrops"] += 1
                else:
                    aks[self.mac]["sent"][1] += [packet.seq];
            except Exception, e:
                #print "s",e
                pass;

        #Transport Layer (UDP, TCP)
        if (packet.proto == 6): element["tcp"] +=1
        elif (packet.proto == 17): element["udp"] +=1
        
        #Application Layer (HTTP, HTTPS)
        #if (packet.sport == 443): element["https"] += 1
        #elif (packet.sport == 80): element["http"] = 1
        if (packet.sport in element["ports"]): element["ports"][packet.sport] += 1
        else: element["ports"][packet.sport] = 1

        #Drop Packets
        #try:
            #if (packet.seq in aks[self.mac][0] or packet.seq in aks[self.mac][1]):
            #    element["drops"]+=1;
            #else:
            #    aks[self.mac][1] += [packet.seq];
        #except Exception, e:
            #print "Error",e
            #pass;

        
        
        #Check HTTP Leaks
        if (packet.dport == 80):
            self.check_leaks(packet)

        #Keep packets in dict type
        #try:
            #If this crashes then entry for this port doesn't exist, so we must create it.
        #    element["type"][str(packet.sport)] += 1
        #except:
        #    element["type"][str(packet.sport)] = 1

        ### Constraint Size of Report to 1000 datapoints ~ 5000s (1.3 hours) = ###
        if (len(self.report) > 1000):
            self.report = self.report[1:]


    def check_leaks(self,packet):
        try:
            if (packet[Raw].load[:4] == "POST"):
                
                raw = packet[Raw].load.lower()
                if ("pass" in raw):
                    print "Leak Found!"
                    r1 = raw[raw.index("host:"):]
                    host = r1[:r1.index("\r\n")].replace("host:","")
                    content = raw[raw.index("content-length:"):]
                    tleak = {"host":host,"content":content}
                    self.leak += [tleak];
        except:
            pass;
        #check if they have something called password or login
        #check host and return host.
        return "TODO"



## Monitor a Real Network ##
def monitor(timeout=None,iface="tap0"):
    if timeout==None:
        sniff(iface=iface,prn=rec_packet)
    else:
        sniff(timeout=timeout,iface=iface,prn=rec_packet)

## Read from a Capture File ##
def fake_monitor(n,capture_file):
    packets = PcapReader(capture_file)
    for packet in packets:
        rec_packet(packet)
    upload_data(); #Just in case data capture was small

## Record a packet into our Client Structure ##    
def rec_packet(packet):
    global clients_names,clients,debug
    try:
        if Client.timesteps == []: Client.timesteps += [packet.time] #[packet.payload.time]

        t = packet.time #t = packet.payload.time #t = time.time()        
        #print t, str(Client.timesteps[-1]);
        ## --- Should we send an Update to Flask Server--- ##
        if (t > Client.timesteps[-1] + timestep):
            upload_data()


        # -------| Record Source |-------
        if packet.src not in clients_names:
            #Add client to our dataset if we haven't seen 'em before.           
            clients_names += [packet.src]
            ##
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
            #traceback.print_exc()
            #if "index" in e: print traceback.print_exc()
            #print packet.show()

## Print Debuggin' Information ##
def print_debuggin_info():
    global clients
    print "---Clients:"
    for c in clients:
        print "  MAC:",c.mac
        print " ",c.report[len(c.report)-1]
        print " "

## POST data to our flask middleman ##
def upload_data():
    global clients,url,endpoint
    try:
        temp = [clients,clients[0].timesteps]
        print temp
        r = requests.post(url+"/"+endpoint,headers={'Content-type':'application/json'},data=jsonpickle.encode(temp))
    except:
        print "Failed to Upload Data"


if __name__ == "__main__":
    if "fake" in sys.argv:
        #Fake Monitor - 
        capture = "capture_examples/kaleo.pcap" #WARNING: PCAP FILES ONLY. (Timing will be off if you are using pcapng files.)
        fake_monitor(600,capture)
    else:
        monitor(timeout,iface)
    #embed()
