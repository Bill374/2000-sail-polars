# NMEA2000 Sailing Performance Logger
An entry in the Pi's crontab file starts logging automatically when the Pi boots up.
```
@reboot python3 /home/RKRLogger/logger.py
```

## Set up before logging
* Listen on the NEMA 2000 bus for a GPS time message.
* Set the system time.
* Set the file name for logging using the current date.
* Open the log file for append and write the column headers.

## Filters
To avoid the log files becoming too large, only messages directly relevant to sailing performance are logged.  All other messages are filtered out.

### Messages included:
The list of messages still needs to be verified.
* 127245, Rudder
  * Angle
  * Position 
* 127250, Vessel Heading
  * Heading
  * Deviation
  * Variation
  * Reference (True/Magnetic)
* 127251, Rate of Turn 
* 127252, Heave
* 127257, Attitude
  * Yaw
  * Pitch
  * Roll
* 128259, Speed
  * Speed Water Referenced
  * Speed Ground Referenced
  * Speed Water Referenced Type
  * Speed Direction
* 129025, Position Rapid Update
  * Latitude
  * Longitude
* 129026, COG & SOG, Rapid Update
  * COG Reference (True/Magnetic)
  * COG
  * SOG
* 129029, GNSS Postion Data
  * Days since January 1, 1970
  * Seconds since midnight
  * Lattitude
  * Longitude
  * Altitude
* 129033, Date and Time _Very infrequent in logged data_
  * Days since January 1, 1970
  * Seconds since midnight
  * Local Offset
* 130306, Wind Data
  * Wind Speed
  * Wind Direction
  * Wind Reference (True/Magnetic/Apparent
* 130577, Direction Data
  * Data Mode
  * COG Reference (True/Magnetic)
  * COG
  * SOG
  * Heading
  * SPeed Through Water 
  * Set
  * Drift

### Messages excluded:
* 59922, Unknown
* 59923, Unknown
* 61183, Unknown
* 65280, Manufacturer Proprietary single-frame non-addressed
* 65305, Unknown
* 65313, Unknown
* 65330, Unknown
* 65341, Simnet: Autopilot Mode
* 126996, Product Information
* 127237, Heading/Track control
* 128267, Water Depth
* 129283, Cross Track Error
* 129284, Navigation Data
* 127285, Magnetic Variation (to be added to analyzer)
* 129539, GNSS DOPs
* 129540, GNSS Sats in View
* 130310, Environmental Parameters
* 130311, Environmental Parameters
* 130316, Temperature Extended Range
* 130822, Unknown
* 130824, B&G: Wind data _Not enough information in analyzer_

## Output
Logging output is written to a plain text file named RKR-yyyy-mm-dd.log
Logging continues in an infinite loop until the logger receives an interupt signal.

## Shutdown
When main power is lost, a monitoring script issues an interupt to the logger.  The pi continues to run on UPS power long enough to complete the shutdown process.<br>
On interupt the logging stops and the file is closed.  What we ultimately want to happen at that point is for the complete log file to be uploaded to Google drive or possibly using bluetooth to a paired phone.
