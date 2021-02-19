#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 18:52:25 2021

@author: wmorland
"""

import datetime
import logging
import subprocess
import can


def start_can_bus():
    """
    Start the the NMEA 2000 network

    Returns
    -------
    can.BusABC

    """

    logger = logging.getLogger('nmea')
    try:
        rc = subprocess.call('sudo ip link set can0 type can bitrate 100000')
        if rc < 0:
            logger.error('Call to ip link set terminated by signal.')
            return None
    except OSError:
        logger.error('Call to ip link set failed.')
        return None

    try:
        rc = subprocess.call('sudo ifconfig can0 up')
        if rc < 0:
            logger.error('Call to ifconfig terminated by signal.')
            return None
    except OSError:
        logger.error('Call to ifconfig failed.')
        return None

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
        rc = subprocess.call('sudo ifconfig can0 down')
        if rc < 0:
            logger.error('Call to ifconfig terminated by signal.')
    except OSError:
        logger.error('Call to ifconfig failed.')
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
    return datetime.datetime.today()
