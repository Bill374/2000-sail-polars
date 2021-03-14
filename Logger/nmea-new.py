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
        subprocess.run('sudo ip link set can0 type can bitrate 100000',
                       check=True)
    except subprocess.CalledProcessError as process_error:
        rc = process_error.returncode
        logger.error('ip link set can0: FAIL')
        logger.error(f'return code = {rc}')
        return None
    logger.info('ip link set can0: SUCCESS')

    try:
        subprocess.run('sudo ifconfig can0 up', check=True)
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
        subprocess.run('sudo ifconfig can0 down', check=True)
    except subprocess.CalledProcessError as process_error:
        rc = process_error.returncode
        logger.error('ifconfig can0 down: FAIL')
        logger.error(f'return code = {rc}')

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


class Message:
    """
    NMEA 2000 message.

    The :class:`~nema.Message` is used to give a NEMA 2000 representation of a
    message rather than the more general CAN representation in can.Message
    """
    __slots__ = (
        'can_message',
        'sof',          # 01 bit - start of frame
        'pty',          # 03 bit - priority
        'pgn',          # 18 bit - parameter group number
        'srr',          # 01 bit - substitute remote request
        'ide',          # 01 bit - identifier extension
        'src',          # 08 bit - source address
        'rtr',          # 01 bit - remote transmission request
        'r1',           # 01 bit - CAN reserved bit 1
        'r2',           # 01 bit - CAN reserved bit 2
        'dlc',          # 04 bit - data length code
        'data',         # 08 byte - data
        )

# plain format of message to be read by canboat analyzer
# timestamp             (time)
# priority              (p)
# pgn                   (pgn)
# source                (s)
# destination           (d)
# number of data bytes  (b)
# up to 8 bytes of data (data)

# time----------------------,p,pgn---,s,d--,b,data-------------------
# 2020-10-04 21:48:20.582346,3,129029,9,255,8,80,2b,b3,6d,48,a0,e2,a8
# 2020-10-04 21:48:20.582912,3,129029,9,255,8,81,2e,80,7e,e4,8c,5e,63
# 2020-10-04 21:48:20.583508,3,129029,9,255,8,82,0d,06,80,16,84,f3,85
# 2020-10-04 21:48:20.584069,3,129029,9,255,8,83,32,f8,f4,70,9e,1c,02
# 2020-10-04 21:48:20.584641,3,129029,9,255,8,84,00,00,00,00,10,fc,0c
# 2020-10-04 21:48:20.585225,3,129029,9,255,8,85,3c,00,78,00,4b,f2,ff
# 2020-10-04 21:48:20.585839,3,129029,9,255,8,86,ff,ff,ff,ff,ff,ff,ff

# The Fast Packet protocol defined in NMEA 2000 provides a means to stream up
# to 223 bytes of data, with the advantage that each frame retains the
# parameter group identity and priority. The first frame transmitted uses 2
# bytes to identify sequential Fast Packet parameter groups and sequential
# frames within a single parameter group transmission. The first byte contains
# a sequence counter to distinguish consecutive transmission of the same
# parameter groups and a frame counter set to frame zero. The second byte in
# the first frame identifies the total size of the parameter group to follow.
# Successive frames use just single data byte for the sequence counter and the
# frame counter.

     {
        "PGN":129029,
        "Id":"gnssPositionData",
        "Description":"GNSS Position Data",
        "Type":"Fast",
        "Complete":true,
        "Length":51,
        "RepeatingFields":3,
        "Fields":[
          {
            "Order":1,
            "Id":"sid",
            "Name":"SID",
            "BitLength":8,
            "BitOffset":0,
            "BitStart":0,
            "Signed":false},
          {
            "Order":2,
            "Id":"date",
            "Name":"Date",
            "Description":"Days since January 1, 1970",
            "BitLength":16,
            "BitOffset":8,
            "BitStart":0,
            "Units":"days",
            "Type":"Date",
            "Resolution":1,
            "Signed":false},
          {
            "Order":3,
            "Id":"time",
            "Name":"Time",
            "Description":"Seconds since midnight",
            "BitLength":32,
            "BitOffset":24,
            "BitStart":0,
            "Units":"s",
            "Type":"Time",
            "Resolution":"0.0001",
            "Signed":false},
          {
            "Order":4,
            "Id":"latitude",
            "Name":"Latitude",
            "BitLength":64,
            "BitOffset":56,
            "BitStart":0,
            "Units":"deg",
            "Type":"Latitude",
            "Resolution":"0.0000000000000001",
            "Signed":true},
          {
            "Order":5,
            "Id":"longitude",
            "Name":"Longitude",
            "BitLength":64,
            "BitOffset":120,
            "BitStart":0,
            "Units":"deg",
            "Type":"Longitude",
            "Resolution":"0.0000000000000001",
            "Signed":true},
          {
            "Order":6,
            "Id":"altitude",
            "Name":"Altitude",
            "Description":"Altitude referenced to WGS-84",
            "BitLength":64,
            "BitOffset":184,
            "BitStart":0,
            "Units":"m",
            "Resolution":1e-06,
            "Signed":true},
          {
            "Order":7,
            "Id":"gnssType",
            "Name":"GNSS type",
            "BitLength":4,
            "BitOffset":248,
            "BitStart":0,
            "Type":"Lookup table",
            "Signed":false,
            "EnumValues":[
              {"name":"GPS","value":"0"},
              {"name":"GLONASS","value":"1"},
              {"name":"GPS+GLONASS","value":"2"},
              {"name":"GPS+SBAS/WAAS","value":"3"},
              {"name":"GPS+SBAS/WAAS+GLONASS","value":"4"},
              {"name":"Chayka","value":"5"},
              {"name":"integrated","value":"6"},
              {"name":"surveyed","value":"7"},
              {"name":"Galileo","value":"8"}]},
          {
            "Order":8,
            "Id":"method",
            "Name":"Method",
            "BitLength":4,
            "BitOffset":252,
            "BitStart":4,
            "Type":"Lookup table",
            "Signed":false,
            "EnumValues":[
              {"name":"no GNSS","value":"0"},
              {"name":"GNSS fix","value":"1"},
              {"name":"DGNSS fix","value":"2"},
              {"name":"Precise GNSS","value":"3"},
              {"name":"RTK Fixed Integer","value":"4"},
              {"name":"RTK float","value":"5"},
              {"name":"Estimated (DR) mode","value":"6"},
              {"name":"Manual Input","value":"7"},
              {"name":"Simulate mode","value":"8"}]},
          {
            "Order":9,
            "Id":"integrity",
            "Name":"Integrity",
            "BitLength":2,
            "BitOffset":256,
            "BitStart":0,
            "Type":"Lookup table",
            "Signed":false,
            "EnumValues":[
              {"name":"No integrity checking","value":"0"},
              {"name":"Safe","value":"1"},
              {"name":"Caution","value":"2"}]},
          {
            "Order":10,
            "Id":"reserved",
            "Name":"Reserved",
            "Description":"Reserved",
            "BitLength":6,
            "BitOffset":258,
            "BitStart":2,
            "Type":"Binary data",
            "Signed":false},
          {
            "Order":11,
            "Id":"numberOfSvs",
            "Name":"Number of SVs",
            "Description":"Number of satellites used in solution",
            "BitLength":8,
            "BitOffset":264,
            "BitStart":0,
            "Signed":false},
          {
            "Order":12,
            "Id":"hdop",
            "Name":"HDOP",
            "Description":"Horizontal dilution of precision",
            "BitLength":16,
            "BitOffset":272,
            "BitStart":0,
            "Resolution":"0.01",
            "Signed":true},
          {
            "Order":13,
            "Id":"pdop",
            "Name":"PDOP",
            "Description":"Probable dilution of precision",
            "BitLength":16,
            "BitOffset":288,
            "BitStart":0,
            "Resolution":"0.01",
            "Signed":true},
          {
            "Order":14,
            "Id":"geoidalSeparation",
            "Name":"Geoidal Separation",
            "Description":"Geoidal Separation",
            "BitLength":32,
            "BitOffset":304,
            "BitStart":0,
            "Units":"m",
            "Resolution":"0.01",
            "Signed":true},
          {
            "Order":15,
            "Id":"referenceStations",
            "Name":"Reference Stations",
            "Description":"Number of reference stations",
            "BitLength":8,
            "BitOffset":336,
            "BitStart":0,
            "Signed":false},
          {
            "Order":16,
            "Id":"referenceStationType",
            "Name":"Reference Station Type",
            "BitLength":4,
            "BitOffset":344,
            "BitStart":0,
            "Type":"Lookup table",
            "Signed":false,
            "EnumValues":[
              {"name":"GPS","value":"0"},
              {"name":"GLONASS","value":"1"},
              {"name":"GPS+GLONASS","value":"2"},
              {"name":"GPS+SBAS/WAAS","value":"3"},
              {"name":"GPS+SBAS/WAAS+GLONASS","value":"4"},
              {"name":"Chayka","value":"5"},
              {"name":"integrated","value":"6"},
              {"name":"surveyed","value":"7"},
              {"name":"Galileo","value":"8"}]},
          {
            "Order":17,
            "Id":"referenceStationId",
            "Name":"Reference Station ID",
            "BitLength":12,
            "BitOffset":348,
            "BitStart":4,
            "Units":null,
            "Signed":false},
          {
            "Order":18,
            "Id":"ageOfDgnssCorrections",
            "Name":"Age of DGNSS Corrections",
            "BitLength":16,
            "BitOffset":360,
            "BitStart":0,
            "Units":"s",
            "Resolution":"0.01",
            "Signed":false}]},


    sof = 0b0                   # 1 BIT SOF
    pty = 0b000                 # 3 BIT Priority
    pgn = 0b000000000000000000  # 18 BIT Parameter Group Number
    srr = 0b0                   # 1 BIT Substitute Remote Request
    ide = 0b1                   # 1 BIT Identifier Extension Bit
    src = 0b00000000            # 8 BIT Source Address
    rtr = 0b0                   # 1 BIT Remote transmission request
    r1 = 0x0                    # 1 BIT CAN reserved bit 1
    r2 = 0x0                    # 1 BIT CAN reserved bit 2
    dlc = 0x0000                # 4 BIT Data Length Code

# can.Message
# timestamp
# arbitration_id
#  - int upto 2^11 or 2^29 for extended_id
# data
#  - byte array length between 0 and 8
# dlc
#  - integer between 0 and 8 representing the frame payload length
# channel
# is_extended_id
#  - bool flag that controls the size of the arbitration id field
#  - always true for NMEA 2000
# is_error_frame
# is_remote_frame
# is_fd
# bitrate_switch
# error_state_indicator

# static void getISO11783BitsFromCanId(unsigned int id, unsigned int * prio, unsigned int * pgn, unsigned int * src, unsigned int * dst)
# {
#   unsigned char PF = (unsigned char) (id >> 16);
#   unsigned char PS = (unsigned char) (id >> 8);
#   unsigned char DP = (unsigned char) (id >> 24) & 1;

#   if (src)
#   {
#     *src = (unsigned char) id >> 0;
#   }
#   if (prio)
#   {
#     *prio = (unsigned char) ((id >> 26) & 0x7);
#   }

#   if (PF < 240)
#   {
#     /* PDU1 format, the PS contains the destination address */
#     if (dst)
#     {
#       *dst = PS;
#     }
#     if (pgn)
#     {
#       *pgn = (DP << 16) + (PF << 8);
#     }
#   }
#   else
#   {
#     /* PDU2 format, the destination is implied global and the PGN is extended */
#     if (dst)
#     {
#       *dst = 0xff;
#     }
#     if (pgn)
#     {
#       *pgn = (DP << 16) + (PF << 8) + PS;
#     }
#   }

# }



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
    gnss_position_recieved = False
    while not gnss_position_recieved:
        msg = can0.recv(10.0)
        arbitration_id = msg.arbitration_id
        # arbitration_id is 28 bits
        # 16-23 PGN High-order byte
        # 08-15 PGN Low-order byte
        # we are looking for PGN = 129029

# PGN 129029 - GNSS Position
# 2020-10-04 21:48:20.582346,3,129029,9,255,8,80,2b,b3,6d,48,a0,e2,a8
# 2020-10-04 21:48:20.582912,3,129029,9,255,8,81,2e,80,7e,e4,8c,5e,63
# 2020-10-04 21:48:20.583508,3,129029,9,255,8,82,0d,06,80,16,84,f3,85
# 2020-10-04 21:48:20.584069,3,129029,9,255,8,83,32,f8,f4,70,9e,1c,02
# 2020-10-04 21:48:20.584641,3,129029,9,255,8,84,00,00,00,00,10,fc,0c
# 2020-10-04 21:48:20.585225,3,129029,9,255,8,85,3c,00,78,00,4b,f2,ff
# 2020-10-04 21:48:20.585839,3,129029,9,255,8,86,ff,ff,ff,ff,ff,ff,ff


 

       msg = can.Message(arbitration_id=0xc0ffee,
                      data=[0, 25, 0, 1, 3, 1, 4, 1],
                      is_extended_id=True)

    

    # decode the message.
    # date and time will be GMT
    # return a python datetime object.

    return datetime.datetime.today()
