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

## External Storage Configuration
You can connect a USB drive to the USB port on the Pi, and mount the file system as an easy method to copy the log files for performance analysis.  By default, the Pi automatically mounts some of the popular file systems such as FAT, NTFS, and HFS+ at the `/media/pi/<HARD-DRIVE-LABEL>` location.

### Step 1 – Plug in the USB Drive

### Step 2 – Identify the File System Type and Unique ID
```
sudo lsblk -o UUID,NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL,MODEL
```
This should produce an output something like this.
```
UUID                                 NAME        FSTYPE  SIZE MOUNTPOINT LABEL  MODEL
                                     sda                29.8G                   Relay_UFD
491A347D4977C5A0                     └─sda1      ntfs   29.8G            USB    
                                     mmcblk0            59.5G                   
4AD7-B4D5                            ├─mmcblk0p1 vfat    256M /boot      boot   
2887d26c-6ae7-449d-9701-c5a4018755b0 └─mmcblk0p2 ext4   59.2G /          rootfs 
```
The USB drive will usually refer to `sda` or `sda1`.  The UUID above is `491A347D4977C5A0`.  The FSTYPE is `ntfs`.  Note these down.
You would need to repeat this step if you wanted to use a different device as the UUID would be different.  
The remaining steps are handled by the install script.  You will need to edit the [DEFAULT] section of `install.cfg` to put in your specific values
```
[DEFAULT]
    usb_directory = /media/usb
    usb_uuid = 491A347D4977C5A0
    usb_fstype = ntfs
```

### Step 3 – Create a Mount Point
A mount point is a directory that will point to the contents of your flash drive. Create a suitable folder :
```
sudo mkdir /media/usb
```
For this example we use `usb` but you can give it whatever name you like.  Now we need to make sure the Pi user owns this folder
```
sudo chown -R pi:pi /media/usb
```

### Step 4 – Manually Mount The Drive
```
sudo mount /dev/sda1 /media/usb -o uid=pi,gid=pi
```
This will mount the drive so that the ordinary pi user can write to it.  Omitting the `-o uid=pi,gid=pi` would mean you could only write to it using `sudo`.

### Step 5 – Un-mounting The Drive
You don’t need to manually un-mount if you shutdown the pi but if you need to remove the drive at any other time you should un-mount it first.  Only the user that mounted the drive can un-mount it.
```
umount /media/usb
```
If you used the fstab file to auto-mount it you will need to use :
```
sudo umount /media/usb
```
If you are paying attention you will notice the command is `umount` NOT `unmount`!

### Step 6 – Auto Mount
When the Pi restarts the mount will be lost and you will need to repeat Step 4. If you want the USB drive to be mounted when the system starts you can edit the fstab file :
```
sudo nano /etc/fstab
```
Then add the following line at the end :
```
UUID=491A347D4977C5A0 /media/usb vfat auto,nofail,noatime,users,rw,uid=pi,gid=pi 0 0
```
The `nofail` option allows the boot process to proceed if the drive is not plugged in.  The `noatime` option stops the file access time being updated every time a file is read from the USB drive. This helps improve performance.

### NTFS

If your storage device uses an NTFS file system, you will only have read-only access to it by default.  To be able to write to the device, you need to install the ntfs-3g driver:
```
sudo apt update
sudo apt install ntfs-3g
```

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
sudo pip install google-auth
sudo pip install google_api-python-client
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

#### [DEFAULT]
In most cases this is the only part of `install.cfg` that you will need to edit.  There are some values in this section that are installation specific.

#### [FILES]
Three options *core*, *test*, *executables*
* _core_ lists the files that are required for the logger and analyser to function.
* _test_ lists files that may optionally be installed to run various tests to ensure everything is functioning as it should.
* _executables_ lists some useful little utilities to be installed on the pi. 

#### [LINUX]
Lists the Linux packages that must be installed for the logger to function.

#### [PYTHON]
Lists additional Python modules that must be installed for the logger code.

#### [BOOT-CONFIG]
Lines to be added to `/boot/config.txt`.  The installer checks to see if the lines are already present and only adds them if they are not there.  The installer is not smart enought to remove any redundant lines if something needs to be changed about the installation.  Removing lines requires manual editing.
```
# Waveshare RS485 CAN HAT mcp2515 kernel driver
dtparam=spi=on
# Waveshare RS485 CAN HAT - 12MHz crystal version
dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=2000000
```

#### [CRONTAB]
Lines to be added to the `/etc/crontab` file so the logger starts automatically when the Pi is booted up.
```
PYTHONPATH=/opt/RKR-Logger
RKRPROCESSLOGS=/home/pi/RKR-process-logs
@reboot root power-monitor &
```

#### [FSTAB]
Lines to be added to `/etc/fstab` file so the USB drive is mounted if it is plugged in when the Pi is booted up.
```
# USB Drive
UUID=%(usb_uuid)s %(usb_directory)s %(usb_fstype)s auto,nofail,noatime,users,rw,uid=pi,gid=pi 0 0
```

#### [ENVIRONMENT]
Variables to be exported to the runtime environment.

#### [GOOGLE]
Service account and authentication information to allow connecting to Google Drive to upload log files.  Authentication uses a private key that essentially gives broad annonymous access to the Google Drive.  The private key should never be disclosed to anyone and it will need to be manually copyed to a secure location on the Pi.
