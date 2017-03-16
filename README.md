<h1>EagleEye</h1>
<h2>Quick and painless wireless real-time monitor</h2>

<h3>Goal</h3>
Simple and easy to use wireless managment software that will allow non-technical "sysadmins" to understand how their networks are being used.

![EagleEye](http://konukoii.com/blog/wp-content/uploads/2017/03/eagle_eye_screenshot.png)

<h3>Requirements</h3>
Run the following commands to install prerequisites:

```
apt-get update
sudo apt-get install python python-pip libboost-all-dev libpcap-dev libssl-dev cmake g++ 
sudo -H pip install -r requirements.txt
```

You will also need: (*check on both links to see how to build).
 - libtins: https://github.com/mfontanini/libtins
 - dot11decrypt: https://github.com/mfontanini/dot11decrypt
 

<h3>How to Run</h3>

**Tested with following Environment:**
- OS: Linux Mint 17.2 'Rafaela' (Mate 32-bit)
- Wireless Adapter: TP-Link TL-WN722N (High Gain 150Mbps) [wlan1]
- Make sure you have all the required packages described above.

**Running the program:**
- Change the necessary values (AP Name, Interface Name) in setup.sh (and possibly packetCapture.py & APFind.py's main function)
- Run ```./setup.sh```
- Run ```sudo python backend.py```
- You should be able to go to localhost:1992 and see a website being hosted there.
- On the website you should be able to simply select your AP and password and hit "monitor"
- Then the packet capture will start. (Notice: the capture currently lasts a few seconds for debuggin purposes).

**Running the program in TEST Mode (w/o packet capture):**
- On backend.py, set ```TESTING=False``` in backend.py.
- On packetCapture.py, set ```capture = "<some path to a .pcap capture file>```.

<h3>Code Division</h3>

- backend.py: Runs a flask server listening on localhost:1992 it recieves requests from the client (get data) and data from the APFind and packetCapture scripts (post data).
- APFind.py: Find APs and then upload to localhost:1992
- packetCapture.py: Capture packets (or read from a pcap file), parsing the important info and uploading to localhost:1992
- template/index.html: HTML website that contains the client info. Pretty much barebones
- client/js/calls.js: All the javascript calls and functions that dynamically update index.html to display charts and info.
- templates/leaks.html: Small helper site to show HTTP leaked information (so as to not crowd the original site)

<br/>
<br/>
<hr>
<h3>Overall Idea</h3>

- First we put our wireless interface in promiscuos mode (meaning it is authenticated to an AP, but we can still read all the other packets from other authenticated users to the same AP).
- We use dot11decrypt to decrypt packets that our interface is reading. These decrypted packets are dropped into a new interaface called TAP0.
- We then use python's library: scapy to read from TAP0.
- Scapy can then do some very minor data analysis on the packets (arange them by users, define their packet type, etc.)
- We wrap scapy over a flask framework so we can do a simple API that a front-end can call.
- We build a simple javascript/html website that can call the flask API get the latest info on the packets, do some further data analysis on them and present them with nice graphs. (The idea of doing more data analysis in the frontend is to avoid overwhelming the python server + it allows us to leave the server running in a raspberry pi and access it from multiple other computers + js/html is way easier to code than other GUI libraries).


