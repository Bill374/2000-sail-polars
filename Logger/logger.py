#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 18:50:30 2021

@author: wmorland
"""

import sys
import logging
import nmea


nmea.zip_logs()
nmea.send_to_drive()

can0 = nmea.start_can_bus()
if can0 is None:
    logging.error('Oops.')
    sys.exit(-1)

gps_time = nmea.get_gps_time(can0)
log_file = gps_time.strftime('%Y%m%d-%H:%M:%S-Log.n2k')

nmea.set_filters(can0)

# start logging in an infinite loop until there is an interupt

# on interupt

nmea.stop_can_bus()
nmea.zip_logs()
nmea.send_to_drive()

# check that the log file was successfully send to Google drive then delete it

sys.exit(0)
