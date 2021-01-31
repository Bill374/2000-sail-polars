# 2000-sail-polars
NMEA2000 message logging and sailing performance analysis

# Still in development.

## Hardware
Designed to be installed and run on: 
* Raspberry Pi Zero W <br>
https://www.raspberrypi.org/documentation/ <br>
Sold by BuyaPie.ca https://www.buyapi.ca/product/raspberry-pi-zero-w/
* Waveshare RS485 CAN HAT <br>
https://www.waveshare.com/wiki/RS485_CAN_HAT <br>
Sold by Waveshare https://www.waveshare.com/rs485-can-hat.htm
* UPS-Lite Power HAT <br>
https://github.com/linshuqin329/UPS-Lite <br>
Sold by Cytron https://www.cytron.io/p-ups-power-hat-for-raspberry-pi-zero
## Software Design
### Logger
The logging software starts on power up and logs only messages from the NMEA2000 bus that are relevant to sailing performance. When a loss of main power is detected the UPS power is used to close the current log file and perform a controlled shutdown of the Pi.
Completed log files are uploaded to a Google Drive for later analysis.
### Analyser
A pre-processing step converts the log files into a performance timeseries with ten records every second.  Each individual record in the series has a value for all the key sailing performance parameters.
Pattern matching logic is used on the performance timeseries to tag key events such as race start, tack start, tack end, gybe start, gybe end, etc.  Other significant events such as sail changes can be tagged manually.
Polar performance is calculated from the tagged performance timeseries.
