from scapy.all import *
import time, copy

timestep = 5 # 5 Seconds (Equivalent to the granularity of the graphs)


### Client Object ###
class Client:

    windowsize = timestep
    template = {'timestamp': None, 'sent': None,'recv': None,'tcp': None,'udp': None,'http': None,'https': None}

    def __init__(self,mac,ip="",name="",os=""):
        self.last_timestamp = [time.time(),time.ctime()] # [Millisecs,Timestamp]
        self.mac = mac   # MAC
        self.ip = ""     # IP
        self.name = ""   # Gotten by Nmap Sweep
        self.os = ""     # Mac, Linux, Windows, Other, N/A
        self.report = [] # Probably a list of dictionaries [{'timestamp':'9:00:00','https':'20%','udp':'80%'},...]

	def record_packet(self,packet):
		t = time.time()
		
		
		if (t < self.last_timestamp[0] + windowsize):
			#Packet is inside window size
			element = self.report[len(self.report)-1][1] #This is a shallow copy		
				
		else:
			#Packet is outside of window size	
			element = [time.ctime(), copy.deepcopy(self.template)]
			self.report += [element] #This is shallow appending

		# { 'timestamp': ,'sent':, 'recieved':,'http':,'udp':...}
		
		#Sent or Recieved
		if (packet.dst == self.mac): element["recv"] +=1
		elif (packet.src == self.mac): element["sent"] +=1

		#Transport Layer (UDP, TCP)
		if (packet.proto == 6):	element["tcp"] +=1
		elif (packet.proto == 17): element["udp"] +=1
		
		#Application Layer (HTTP, HTTPS)
		if (packet.sport == 443): element["https"] += 1
		elif (packet.sport == 80): element["http"] = 1

### Data Storage ###
class Dataset:
    window = timestep
    
    def __init__(self):
        self.clients = []
        self.APs = []
        self.client_names = []

	def record_packet(self,packet):
		
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
			self.clients[self.clients_names.index(packet.src)].record_packet(packet)

    def sniff(self,timeout=None,iface="tap0"):
		sniff(timeout=timeout,iface=iface,prn=self.record_packet)
    
    def os_fingerprint(self,src):
        print "TODO! Check the nmap fingerprint module to define clients"
        return None;
    
    def ap_find(self):
        print "TODO! Check beacons to find nearby APs"
        return None;



if __name__ == "__main__":
    dataset = Dataset()
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


