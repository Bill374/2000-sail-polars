#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 18:52:25 2021

@author: wmorland
"""

import logging
import subprocess
import can
import cannew
from datetime import datetime


def start_can_bus():
    """
    Start the the NMEA 2000 network

    Returns
    -------
    can.BusABC

    """

    logger = logging.getLogger('nmea')

    try:
        subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'type', 'can',
                        'bitrate', '100000'],
                       check=True)
    except subprocess.CalledProcessError as process_error:
        rc = process_error.returncode
        logger.error('ip link set can0: FAIL')
        logger.error(f'return code = {rc}')
        return None
    logger.info('ip link set can0: SUCCESS')

    try:
        subprocess.run(['sudo', 'ifconfig', 'can0', 'up'], check=True)
    except subprocess.CalledProcessError as process_error:
        rc = process_error.returncode
        logger.error('ifconfig can0 up: FAIL')
        logger.error(f'return code = {rc}')
        return None
    logger.info('ifconfig can0 up: SUCCESS')

    return can.interface.Bus(channel='can0', bustype='socketcan_ctypes')


def stop_can_bus():
    """
    Stop the NMEA 2000 network.

    Returns
    -------
    None.

    """

    logger = logging.getLogger('nmea')
    try:
        subprocess.run(['sudo', 'ifconfig', 'can0', 'down'], check=True)
    except subprocess.CalledProcessError as process_error:
        rc = process_error.returncode
        logger.error('ifconfig can0 down: FAIL')
        logger.error(f'return code = {rc}')
    logger.info('ifconfig can0 down: SUCCESS')

    return None


def set_filters(can0):
    """
    Set filters on the NMEA 2000 network.

    The filters ensure that only messages directly relevent to sailing
    performance are logged.

    Parameters
    ----------
    can0 : can.BusABC
        The can bus object connected to the NMEA 2000 network to be filtered

    Returns
    -------
    None.

    """

    logger = logging.getLogger('nema')
    logger.info('Adding filters')
    filters = [{"can_id": 0x11, "can_mask": 0x21, "extended": False}]
    can0.set_filters(filters)


def get_gps_time(can0, wait=100):
    """
    Return the current GPS time from the NMEA network.

    If no GPS time message is heard on the network after a specified number of
    seconds an exception is thrown.

    Parameters
    ----------
    can0 : can.BusABC
    wait : int, optional
        The number of seconds to wait for a GPS time message before giving up
        and thoring an exception. The default is 100.

    Returns
    -------
    datetime.

    """

    logger = logging.getLogger('nema')
    logger.info('Get GPS Time')
    return datetime.datetime.today()


def capture_can_messages(can0):
    """
    Capture all messages from the CAN Bus.

    Messages are captured in series of log files, once the max file size is
    reached a new file is started.  In this simple initial version there is no
    filtering on the messages.

    Parameters
    ----------
    can0 : can.BusABC

    Returns
    -------
    None.

    """
    logger = logging.getLogger('nmea')
    logger.info('Capture CAN messages')

    file_size = 500
    log_file = 'foo.n2k'

    can0 = start_can_bus()
    can_logger = cannew.Logger(base_filename=log_file)

    try:
        while True:
            msg = can0.recv(1)
            if msg is not None:
                can_logger(msg)
    except KeyboardInterrupt:
        pass
    finally:
        stop_can_bus()
        can_logger.stop()
