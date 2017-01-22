<h1>EagleEye</h1>
<h2>Quick and painless wireless real-time monitor</h2>

<h3>Goal</h3>
Simple and easy to use wireless managment software that will allow non-technical "sysadmins" to understand how their networks are being used.


<h3>Requirements</h3>
Run the following commands to install prerequisites:
```
apt-get update
sudo apt-get install python python-pip libboost-all-dev libpcap-dev libssl-dev cmake g++ 
pip install -r requirements.txt
```
You will also need:
 - libtins: https://github.com/mfontanini/libtins
 - dot11decrypt: https://github.com/mfontanini/dot11decrypt

<h3>Overall Idea</h3>
- First we put our wireless interface in promiscuos mode (meaning it is authenticated to an AP, but we can still read all the other packets from other authenticated users to the same AP).
- We use dot11decrypt to decrypt packets that our interface is reading. These decrypted packets are dropped into a new interaface called TAP0.
- We then use python's library: scapy to read from TAP0.
- Scapy can then do some very minor data analysis on the packets (arange them by users, define their packet type, etc.)
- We wrap scapy over a flask framework so we can do a simple API that a front-end can call.
- We build a simple javascript/html website that can call the flask API get the latest info on the packets, do some further data analysis on them and present them with nice graphs. (The idea of doing more data analysis in the frontend is to avoid overwhelming the python server + it allows us to leave the server running in a raspberry pi and access it from multiple other computers + js/html is way easier to code than other GUI libraries).

<h3>To-Do</h3>
1. Properly capture and decrypt 802.11 packets within network (using promiscuos mode).
2. Parse through data to obtain relevant info (clients, packet types, etc.)
3. Wrap scapy with flask
4. Build html/js frontend for client

