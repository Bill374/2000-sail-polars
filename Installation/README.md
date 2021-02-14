# NMEA2000 Sail Polars Installation Instructions

Instructions to set up Raspberry Pi Zero, UPS and CAN HAT prior to running the logger application.  Eventually this should be handled by an automated install script.

## Pi Zero configuration

## Installing the UPS Power Mangement

The Cytron UPS Power HAT includes The HAT comes with on-board LEDs to show the status of the battery at full capacity or charging.  A MAX17040 fuel gauge on the HAT adopted provides accurate power detection.  The Raspberry Pi is able to get information on battery capacity and battery voltage directly via I2C communication.

Enable the I2C on Raspberry Pi proccessor `sudo raspi-config`

Install I2C tools `sudo apt-get install i2c-tools`

Check the tools installation `sudo i2cdetect -l`

Check the address of the I2C decice `sudo i2cdetect -y -a 1`. The address of MAX17048 should be 0x36

### Battery status checks

#### Battery capacity

To check the battery capacity `sudo i2cget -f -y 1 0x36 4 w`. The value is returned in hex.

> 0x853d

"0x853d" represents the battery capacity, but some conversion is needed.

> Swap the high byte and low byte to get "0x3d85" after swapping. <br>
> Convert "0x3d85" into decimal，0x3d85 = 15749 <br>
> Divide by 256 to get the percentage of full capacity, 15749/256 = 61.52 <br>

The battery capacity is 61.52%.

#### Battery voltage

To check the voltage reading `sudo i2cget -f -y 1 0x36 2 w`.  The value is returned in hex.

> 0xb0bc

"0xb0bc" represents the battery voltage, but again some conversion is needed. 

> Swap the high byte and low byte to get "0xb980" after swapping. <br>
> Convert "0xbcb0" to decimal, 0xbcb0 = 47488 <br>
> Apply a scaling factor, 48304 * 78.125 / 1000000 = 3.71 <br>

The battery voltage is 3.71V

## Setting up the CAN HAT

### MCP2515 Setup
Edit /boot/config.txt to make sure the mcp2515 kernel driver is open <br>
Add the following lines: 
```
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=25,spimaxfrequency=1000000
```
Then restart the raspberry pi `sudo reboot`

## Python Dependencies

### Install required python libraries:
```
sudo apt-get install python-pip
sudo pip install python-can
sudo pip install RPi.GPIO
sudo pip install smbus
```
## Installing the logger

### Download a file from GitHub

With the Pi Zero connected to WiFi code files can be downloaded directly from GitHub.
```
curl --output Readme https://raw.githubusercontent.com/Bill374/2000-sail-polars/master/Installation/Readme.md
```

`/master/` is the branch of the repository
`/Installation/` is a directory path
`Readme.md` is this file
