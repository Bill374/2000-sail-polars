#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 18:52:25 2021

@author: wmorland
"""

import logging
import subprocess
import can
from base64 import b64encode
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
    log_file = 'foo'

    can0 = start_can_bus()
    can_logger = can.SizedRotatingLogger(base_filename=log_file,
                                         max_bytes=file_size)

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


class N2KWriter(can.BaseIOHandler, can.Listener):
    """
    Writes a comma separated text file with a line for each NMEA2000 message.

    The file format matches the Plain format which can be read by the canboat
    Analyzer.  At some point we might include another writer which outputs
    NMEA2000 Fast format where PGNs that span multiple CAN messages are
    condensed into a single line.

    The output file includes a header line.

    The columns are as follows:
    ================ ======================= =======================
    name of column   format description      example
    ================ ======================= =======================
    timestamp        yyyy-mm-dd:hh:mm:ss     2011-11-24-22:42:04.388
    priority         int                     2
    pgn              int                     127251
    source           int                     12
    destination      int                     255
    dlc              int                     8
    data             base64 encoded          7d,0b,7d,02,00,ff,ff,ff
    ================ ======================= =======================

    Each line is terminated with a platform specific line separator.
    """

    def __init__(self, file, append=False):
        """
        :param file: a path-like object or a file-like object to write to.
                     If this is a file-like object, is has to open in text
                     write mode, not binary write mode.
        :param bool append: if set to `True` messages are appended to
                            the file and no header line is written, else
                            the file is truncated and starts with a newly
                            written header line
        """
        mode = 'a' if append else 'w'
        super(N2KWriter, self).__init__(file, mode=mode)

        # Write a header row
        if not append:
            self.file.write('timestamp,priority,pgn,source,destination,dlc,'
                            'data\n')

    def on_message_received(self, msg):
        """Write message to file in NMEA2000 plain format."""
        assert msg.is_extended_id  # NEMA2000 messages are always extended ID
        assert msg.dlc == 8        # NEMA2000 messages always have 8 data bytes

        # NMEA2000 Masks for 29 bit arbitration ID
        PRIORITY =  0b11100_00000000_00000000_00000000
        PDU_F =     0b00000_11111111_00000000_00000000
        PDU_S =     0b00000_00000000_11111111_00000000
        SHORT_PGN = 0b00011_11111111_00000000_00000000
        LONG_PGN =  0b00011_11111111_11111111_00000000
        SOURCE =    0b00000_00000000_00000000_11111111

        # Pick apart the arbitration ID into the separate NMEA2000 fields
        priority = (msg.arbitration_id & PRIORITY) >> 26
        pdu_f = (msg.arbitration_id & PDU_F) >> 16
        if pdu_f <= 239:
            # The message has a specific destination
            destination = (msg.arbitration_id & PDU_S) >> 8
            pgn = (msg.arbitration_id & SHORT_PGN) >> 16
        else:
            destination = 255
            pgn = (msg.arbitration_id & LONG_PGN) >> 8
        source = msg.arbitration_id & SOURCE

        row = ','.join([
            datetime.fromtimestamp(msg.timestamp).strftime('%Y-%m-%dT%H:%M:%SZ'),
            str(priority),
            str(pgn),
            str(source),
            str(destination),
            str(msg.dlc),
            b64encode(msg.data).decode('utf8')
        ])
        dlc = msg.dlc
        data = msg.data
        while dlc:
            row = ','.join([row, format(data & 0xFF, 'x')])
            data >> 8
            dlc -= 1
        self.file.write(row)
        self.file.write('\n')


class N2KReader(can.BaseIOHandler):
    """
    Iterator over CAN messages from a .n2k file.

    Files are generated by :class:'nmea.N2KWriter` or must use the same
    format as described there.  Assumes that there is a header and skips the
    first line.
    Any line separator is accepted.
    """

    def __init__(self, file):
        """
        :param file: a path-like object or as file-like object to read from
                     If this is a file-like object, is has to opened in text
                     read mode, not binary read mode.
        """
        super(N2KReader, self).__init__(file, mode='r')
