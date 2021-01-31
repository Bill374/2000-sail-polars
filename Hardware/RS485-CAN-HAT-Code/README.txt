
Using this routine requires first installing the library:
sudo apt-get install python3-pip
sudo pip3 install python-can

Then make sure your mcp2515 kernel driver is open:
sudo vi /boot/config.txt

And add the following: 
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=2000000

Then restart the raspberry pi：
sudo reboot

send run:
sudo python3 send.py

Receiving run:
sudo python3 receive.py

You will see the following:
Timestamp: 1527240783.548918        ID: 0123    S          DLC: 8    00 01 02 03 04 05 06 07
