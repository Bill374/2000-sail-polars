# Garmin GPS Glow
Garmin GPS Glow is a Bluetooth GPS receiver.  It does not form part of the hardware needed for running the logger, we just used it as a convenient way to get GPS information to put on the NMEA 2000 Bus for testing.

## Set up
### Install required packages

Linux packages installed by the installer
* bluez 
* gpsd 
* gpsd-clients

Python modules installed by the installer
* pyserial
* pynmea2

### Initial bluetooth pairing.
Find the MAC address of the 
```
hcitool scan
Scanning ...
        10:C6:FC:F5:5D:73      Garmin GLO #55d73
```
Use *bluetoothctl* to pair with the MAC address and make it trusted so the pairing happens automatically in future 
```
sudo bluetoothctl
agent on
agent-default
discoverable on
scan on
pair xx:xx:xx:xx:xx:xx
trust xx:xx:xx:xx:xx:xx
```

### Map to a serial port producing NMEA0183 messages
I think we have to do this everytime on start up.  The killall and rm commands might not be needed but they make sure everything is clean before we start.
```
sudo killall gpsd
sudo rm /run/gpsd.sock
gpsd -n /dev/rfcomm0
```

Check everything is working with `gpsmon /dev/rfcomm0`
```
pi-two:/dev/rfcomm0 9600 8N1  NMEA0183>
┌──────────────────────────────────────────────────────────────────────────────┐
│Time: 2021-03-14T18:52:01.200Z Lat:  43 39' 04.01825" Non:  79 30' 24.04248" W│
└───────────────────────────────── Cooked TPV ─────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────┐
│ GPRMC GPGGA GPVTG GPGSA GPGSV PGRMT                                          │
└───────────────────────────────── Sentences ──────────────────────────────────┘
┌──────────────────┐┌────────────────────────────┐┌────────────────────────────┐
│Ch PRN  Az El S/N ││Time:      185201.2         ││Time:      185201.2         │
│ 0 138 217 32  33 ││Latitude:    4339.06971 N   ││Latitude:  4339.06971       │
│ 1  30 306 45  24 ││Longitude:  07930.40708 W   ││Longitude: 07930.40708      │
│ 2  27  48 33  38 ││Speed:     000.11           ││Altitude:  119.6            │
│ 3   7 259 81  24 ││Course:    140.0            ││Quality:   1   Sats: 08     │
│ 4   8  65 73  29 ││Status:    A       FAA: A   ││HDOP:      0.9              │
│ 5  71  70 62  19 ││MagVar:    010.5W           ││Geoid:     -36.4            │
│ 6  76  58 55  23 │└─────────── RMC ────────────┘└─────────── GGA ────────────┘
│ 7  66 325 49  26 │┌────────────────────────────┐┌────────────────────────────┐
│ 8  75 167 44  17 ││Mode: A3 Sats: 30 27 7 8 71 ││UTC:           RMS:         │
│ 9  21 135 33  26 ││DOP: H=0.9   V=1.0   P=1.4  ││MAJ:           MIN:         │
│10   9 208 19  25 ││TOFF: -0.000712090          ││ORI:           LAT:         │
│11  28 274 18  21 ││PPS:                        ││LON:           ALT:         │
└────── GSV ───────┘└──────── GSA + PPS ─────────┘└─────────── GST ────────────┘
```
