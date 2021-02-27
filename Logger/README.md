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
* 127250, Vessel Heading
* 127285, Magnetic Variation
* 1282159, Speed - _not found in log file_
* 129025, Position Rapid Update
* 129029, GNSS Postion Data
* 129033, Date and Time
* 130306, Wind Data
* 130577, Direction Data

### Messages excluded:
* 59922
* 59923
* 61183
* 65280
* 65305
* 65313
* 65330
* 65341
* 126996
* 127237
* 127251
* 127252
* 127257
* 128259
* 128267
* 129025
* 129026
* 129283
* 129284
* 129539
* 129540
* 130310
* 130311
* 130316
* 130822
* 130824

## Output
Logging output is written to a plain text file named RKR-yyyy-mm-dd.log
Logging continues in an infinite loop until the logger receives an interupt signal.

## Shutdown
When main power is lost, a monitoring script issues an interupt to the logger.  The pi continues to run on UPS power long enough to complete the shutdown process.<br>
On interupt the logging stops and the file is closed.  What we ultimately want to happen at that point is for the complete log file to be uploaded to Google drive or possibly using bluetooth to a paired phone.
