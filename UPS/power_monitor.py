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


def main():
    logger = logging.getLogger('power_monitor')
    logger.info('Start external power monitoriing.')
    ups = ups_lite.UPS()
    shutdown_started = False

    try:
        while True:
            sleep(5)
            if not shutdown_started and not ups.external_power():
                logger.info('External power disconnected.')
                logger.info('Starting shutdown process.')
                shutdown_started = True
                # Any actions we need to take before shutdown go here
                # halt, poweroff, reboot
                rc = os.system('halt')
                if rc != 0:
                    logger.error(f'Shutdown failed. return code = {rc}')
                    return rc
                logger.info('Shutdown process started successfully.')
                return 0
    except KeyboardInterrupt:
        logger.info('Interupted and terminated.')
        return 0


if __name__ == '__main__':
    log_dir = os.getenv('RKRPROCESSLOGS')
    logging.basicConfig(filename=f'{log_dir}power_monitor.log',
                        filemode='w',
                        level=logging.INFO)
    logging.shutdown()
    main()
