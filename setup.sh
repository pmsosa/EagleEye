sudo service avahi-daemon stop
sudo service network-manager stop
sudo airmon-ng start wlan1 11
sudo iwconfig wlan1 channel 11
sudo ./dot11decrypt-master/build/dot11decrypt mon0 'wpa:BlueMix:Kraken02'
