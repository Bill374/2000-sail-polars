#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 19:24:20 2021

@author: wmorland

Script to monitor the external power to the UPS and shut the Pi down gracefully
if it is disconnected.  External power is checked once every five seconds.

This script is automatically run whenever the Pi is rebooted.
"""
from time import sleep
import os
import logging
import ups_lite

logging.info('Start external power monitoriing.')
ups = ups_lite.UPS()
shutdown_started = False

try:
    while True:
        sleep(5)
        if not shutdown_started and not ups.external_power():
            logging.info('External power disconnected.')
            logging.info('Starting shutdown process.')
            shutdown_started = True
            # Any actions we need to take before shutdown go here
            os.system('systemctl poweroff')
except KeyboardInterrupt:
    logging.info('power_monitor.py interupted and terminated.')
