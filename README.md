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

<h3>To-Do</h3>
1. Properly capture and decrypt 802.11 packets within network (using promiscuos mode).
2. Parse through data to obtain relevant info (clients, packet types, etc.)
3. 

