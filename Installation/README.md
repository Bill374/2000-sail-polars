# NMEA2000 Sail Polars Installation Instructions

Instructions to set up Raspberry Pi Zero, UPS and CAN HAT prior to running the logger application.  Most of this is handled by an automated install script, but is it useful to know what that script is doing.

`install.cfg` can be edited to control much of the behaviour of the install script.

## Pi Zero configuration

The initial basic set up of the Pi Zero requires some manual steps.
* step 1
* step 2

## Installing the UPS Power Mangement

The UPS-Lite Power HAT comes with on-board LEDs to show the status of the battery at full capacity or charging.  A MAX17040 fuel gauge on the HAT provides accurate power detection.  The Raspberry Pi is able to get information on battery capacity and battery voltage directly via I2C communication. 

Enable the I2C on Raspberry Pi proccessor `sudo raspi-config` **_MANUAL_**

Install I2C tools `sudo apt-get install i2c-tools`. See `[LINUX]` section in 'install.cfg'.

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

#### External power supply

GPIO pin 04 (BCM numbering} monitors the state of the external power supply (connected or not connected.)
 
## Setting up the CAN HAT

### MCP2515 Setup
Edit /boot/config.txt to make sure the mcp2515 kernel driver is open <br>
Add the following lines: 
```
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=1000000
```
Then restart the raspberry pi `sudo reboot`

**_IMPORTANT_** The oscillator value must be set correctly o match the crystal on the CAN HAT.  Older versions are 8Mz `oscillator=8000000`, newer versions are 12Mz `oscilator=12000000`. Setting the wrong value can cause the NMEA2000 bus to become unstable when the logger is connected.

See section `[BOOT-CONFIG]` in `install.cfg`

## Python Dependencies

Not all the python modules required for the logger and analyser are installed in the basic Pi Zero image.  Make sure `pip` is installed on the Pi and then use it to install the required modules.

```
sudo apt-get install python-pip
```

See section '[LINUX]` in 'install.cfg'

### Install required python libraries:

```
sudo pip install python-can
sudo pip install RPi.GPIO
sudo pip install smbus
```

See section '[PYTHON]` in `install.cfg'

## Installing the logger

### Download a file from GitHub

With the Pi Zero connected to WiFi files can be downloaded directly from GitHub using curl.  In order to start the install process two files will need to be retrieved this way. 
```
curl --output pi_install.py https://raw.githubusercontent.com/Bill374/2000-sail-polars/main/Installation/pi_install.py?RANDOM
curl --output install.cfg https://raw.githubusercontent.com/Bill374/2000-sail-polars/main/Installation/install.cfg?RANDOM

```

`/main/` is the branch of the repository
`/Installation/` is a directory path
`pi_install.py` is the file
`?RANDOM` prevents any previously cached version of the file from being used and ensures that the latest copy is always brought back from the server.

### install.cfg

Much of the behaviour of the installer is driven by the various sections of `install.cfg`.  This file can be edited to modify the installer behaviour without the need for code changes.

#### [FILES]
To options *core* and *test*
* _core_ lists the files that are required for the logger and analyser to function.
* _test_ lists files that may optionally be installed to run various tests to ensure everything is functioning as it should.

#### [LINUX]
Lists the Linux packages that must be installed for the logger to function.

#### [PYTHON]
Lists additional Python modules that must be installed for the logger code.

#### [BOOT-CONFIG]
Lines to be added to `/boot/config.txt`.  The installer checks to see if the lines are already present and only adds them if they are not there.  The installer is not smart enought to remove any redundant lines if something needs to be changed about the installation.  Removing lines requires manual editing.

#### [CRONTAB]
Lines to be added to the `crontab` files so the logger starts automatically when the Pi is booted up.
